import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";

import { chromium } from "playwright";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const port = Number(process.env.BROWSER_CHECK_PORT || 4178);
const baseUrl = `http://127.0.0.1:${port}`;
const server = spawn(
  process.env.PYTHON || "python3",
  ["-m", "http.server", String(port), "--bind", "127.0.0.1", "--directory", "docs"],
  { cwd: root, stdio: "ignore" },
);

async function waitForServer() {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    try {
      const response = await fetch(baseUrl);
      if (response.ok) return;
    } catch {
      // The server may still be starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Dashboard server did not start at ${baseUrl}`);
}

async function waitForStatus(page, text) {
  await page.waitForFunction(
    (expected) => document.getElementById("filter-status")?.textContent?.includes(expected),
    text,
  );
}

async function selectFourFilters(page, { month, account, issue, company }) {
  await page.locator("#month-filter").selectOption({ label: month });
  await page.locator("#subproduct-filter").selectOption({ label: account });
  await page.locator("#issue-filter").selectOption({ label: issue });
  await page.locator("#company-filter").selectOption({ label: company });
}

let browser;
try {
  await waitForServer();
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));

  for (const width of [360, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await waitForStatus(page, "84,194 of 84,194 complaints shown");

    assert.equal(await page.locator("h1").innerText(), "Consumer Complaint Operations Dashboard");
    assert.equal(await page.locator("#metric-total").innerText(), "84,194");
    assert.equal(await page.locator("canvas").count(), 4);
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      true,
      `${width}px page has horizontal overflow`,
    );
    assert.equal(
      await page.locator("canvas").evaluateAll((nodes) =>
        nodes.every((node) => node.getBoundingClientRect().width > 0 && node.getBoundingClientRect().height > 0),
      ),
      true,
      `${width}px charts did not render`,
    );
    assert.equal(
      await page.locator(".filters select, .filters button").evaluateAll((nodes) =>
        nodes.every((node) => node.getBoundingClientRect().height >= 44),
      ),
      true,
      `${width}px filter controls are too small`,
    );

    const bodyText = (await page.locator("body").innerText()).toLowerCase();
    for (const banned of [
      "sha-256",
      "independent portfolio project",
      "no organizational endorsement",
      "model accuracy",
      "deterministic rule",
    ]) {
      assert.equal(bodyText.includes(banned), false, `Public UI contains ${banned}`);
    }

    const columns = await page.locator(".chart-grid--two").evaluate(
      (node) => getComputedStyle(node).gridTemplateColumns.split(" ").length,
    );
    assert.equal(columns, width >= 901 ? 2 : 1, `${width}px chart grid is incorrect`);

    if (process.env.UPDATE_SCREENSHOTS === "1") {
      const label = width === 360 ? "mobile-360" : width === 768 ? "tablet-768" : "desktop-1440";
      await page.screenshot({ path: join(root, "evidence", "screenshots", `${label}.jpg`), fullPage: true });
    }
  }

  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await waitForStatus(page, "84,194 of 84,194 complaints shown");

  await page.locator("#issue-filter").selectOption({ label: "Managing an account" });
  await waitForStatus(page, "44,959 of 84,194 complaints shown");
  assert.match(await page.locator("#metric-concentration-label").innerText(), /SUB-ISSUE/);

  await page.locator("#filters button[type='reset']").click();
  await waitForStatus(page, "84,194 of 84,194 complaints shown");

  await selectFourFilters(page, {
    month: "Jan 2025",
    account: "Checking account",
    issue: "Managing an account",
    company: "BANK OF AMERICA, NATIONAL ASSOCIATION (6,680)",
  });
  await waitForStatus(page, "281 of 84,194 complaints shown");
  assert.equal(await page.locator("#metric-total").innerText(), "281");

  await page.locator("#filters button[type='reset']").click();
  await waitForStatus(page, "84,194 of 84,194 complaints shown");

  await selectFourFilters(page, {
    month: "Feb 2025",
    account: "Checking account",
    issue: "Problem caused by your funds being low",
    company: "JPMORGAN CHASE & CO. (8,937)",
  });
  await waitForStatus(page, "29 of 84,194 complaints shown");
  assert.match(await page.locator("#decision-finding").innerText(), /Small base: 29/);
  assert.match(await page.locator("#decision-action").innerText(), /too small for reliable percentages/i);

  await page.locator("#filters button[type='reset']").click();
  await waitForStatus(page, "84,194 of 84,194 complaints shown");

  await selectFourFilters(page, {
    month: "Jan 2025",
    account: "CD (Certificate of Deposit)",
    issue: "Closing an account",
    company: "NAVY FEDERAL CREDIT UNION (10,606)",
  });
  await waitForStatus(page, "0 of 84,194 complaints shown");
  assert.equal(await page.locator("#metric-total").innerText(), "0");
  assert.equal(await page.locator("#decision-finding").innerText(), "No complaints match the selected filters.");

  await page.locator("#filters button[type='reset']").click();
  await waitForStatus(page, "84,194 of 84,194 complaints shown");
  await page.reload({ waitUntil: "networkidle" });
  await waitForStatus(page, "84,194 of 84,194 complaints shown");
  await page.keyboard.press("Tab");
  assert.equal(
    await page.evaluate(() => document.activeElement?.classList.contains("skip-link")),
    true,
    "Skip link is not first in the keyboard order",
  );

  await page.locator(".data-table-details").first().locator("summary").click();
  assert.equal(await page.locator("#volume-data-table tbody tr").count(), 12);
  assert.equal(
    await page.locator("a[href='https://www.consumerfinance.gov/data-research/consumer-complaints/']").count() >= 1,
    true,
  );
  assert.equal(
    await page.locator("a[href='https://github.com/Duckky153/consumer-complaint-operations']").count(),
    1,
  );

  const directPage = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await directPage.goto(pathToFileURL(join(root, "docs", "index.html")).href, { waitUntil: "load" });
  await waitForStatus(directPage, "84,194 of 84,194 complaints shown");
  assert.equal(await directPage.locator("#metric-total").innerText(), "84,194");
  await directPage.close();

  assert.deepEqual(consoleErrors, [], `Console errors: ${consoleErrors.join(" | ")}`);
  assert.deepEqual(pageErrors, [], `Page errors: ${pageErrors.join(" | ")}`);
  console.log("Browser check passed: 3 responsive views, filters, reset, small-base, empty-state, keyboard, tables, links, and direct-file loading.");
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
}
