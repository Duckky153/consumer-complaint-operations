"use strict";

const state = {
  payload: null,
  records: [],
  charts: {},
  filters: {
    received_month: null,
    sub_product: null,
    issue: null,
    company: null,
  },
};

const numberFormat = new Intl.NumberFormat("en-US");
const percentFormat = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});
const monthFormat = new Intl.DateTimeFormat("en-US", {
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});

const palette = {
  ink: "#171717",
  white: "#ffffff",
  dark: "#454545",
  mid: "#858585",
  light: "#b8b8b8",
  pale: "#dedede",
  grid: "#e4e6e8",
  paper: "#f3f4f4",
};

const MIN_INTERPRETIVE_COUNT = 30;

function canInterpret(count) {
  return count >= MIN_INTERPRETIVE_COUNT;
}

function formatPercent(value) {
  return `${percentFormat.format(value)}%`;
}

function formatMonth(value) {
  return monthFormat.format(new Date(`${value}-01T00:00:00Z`));
}

function wrapChartLabel(value, maximumLineLength = 24) {
  const words = value.split(" ");
  const lines = [];
  let current = "";
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length <= maximumLineLength) {
      current = candidate;
    } else {
      if (current) {
        lines.push(current);
      }
      current = word;
    }
  }
  if (current) {
    lines.push(current);
  }
  if (lines.length <= 2) {
    return lines;
  }
  return [lines[0], `${lines[1].slice(0, maximumLineLength - 1)}…`];
}

function buildChartAriaLabel(title, items) {
  return items.length
    ? `${title}. ${items.join("; ")}.`
    : `${title}. No data matches the selected filters.`;
}

function columnIndex(name) {
  return state.payload.meta.record_columns.indexOf(name);
}

function dictionaryValue(name, index) {
  return state.payload.dictionaries[name][index];
}

function aggregate(rows, keyName) {
  const index = columnIndex(keyName);
  const counts = new Map();
  for (const row of rows) {
    const key = row[index];
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return [...counts.entries()]
    .map(([key, count]) => ({
      key,
      label: dictionaryValue(keyName, key),
      count,
    }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
}

function aggregateRates(rows, keyNames) {
  const keys = keyNames.map(columnIndex);
  const timelyIndex = columnIndex("is_timely");
  const reliefIndex = columnIndex("has_relief");
  const groups = new Map();

  for (const row of rows) {
    const composite = keys.map((index) => row[index]).join("|");
    if (!groups.has(composite)) {
      groups.set(composite, {
        keys: keys.map((index) => row[index]),
        count: 0,
        timely: 0,
        relief: 0,
      });
    }
    const group = groups.get(composite);
    group.count += 1;
    group.timely += row[timelyIndex];
    group.relief += row[reliefIndex];
  }

  return [...groups.values()]
    .map((group) => ({
      labels: group.keys.map((key, position) =>
        dictionaryValue(keyNames[position], key),
      ),
      count: group.count,
      timelyCount: group.timely,
      notTimelyCount: group.count - group.timely,
      timelyRate: (100 * group.timely) / group.count,
      notTimelyRate: (100 * (group.count - group.timely)) / group.count,
      reliefCount: group.relief,
      reliefRate: (100 * group.relief) / group.count,
    }))
    .sort((a, b) => b.count - a.count || a.labels[0].localeCompare(b.labels[0]));
}

function currentRows() {
  return state.records.filter((row) =>
    Object.entries(state.filters).every(([name, selected]) => {
      if (selected === null) {
        return true;
      }
      return row[columnIndex(name)] === selected;
    }),
  );
}

function isDefaultView() {
  return Object.values(state.filters).every((value) => value === null);
}

function rowsMatchingLabel(rows, dimension, label) {
  const index = columnIndex(dimension);
  const code = state.payload.dictionaries[dimension].indexOf(label);
  return code === -1 ? [] : rows.filter((row) => row[index] === code);
}

function median(values) {
  if (!values.length) {
    return 0;
  }
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2
    ? sorted[middle]
    : (sorted[middle - 1] + sorted[middle]) / 2;
}

function conciseCompanyLabel(value) {
  const labels = {
    "NAVY FEDERAL CREDIT UNION": "Navy Federal",
    "CAPITAL ONE FINANCIAL CORPORATION": "Capital One",
  };
  return labels[value] || value;
}

function calculateSummary(rows) {
  if (!rows.length) {
    return {
      count: 0,
      notTimelyCount: 0,
      timelyRate: 0,
      notTimelyRate: 0,
      reliefCount: 0,
      reliefRate: 0,
      concentrationCount: 0,
      concentrationRate: 0,
    };
  }

  const timelyIndex = columnIndex("is_timely");
  const reliefIndex = columnIndex("has_relief");
  const concentrationDimension =
    state.filters.issue === null ? "issue" : "sub_issue";
  const concentrationGroups = aggregate(rows, concentrationDimension);
  const leadingCount = concentrationGroups[0]?.count || 0;
  const timelyCount = rows.reduce(
    (total, row) => total + row[timelyIndex],
    0,
  );
  const reliefCount = rows.reduce(
    (total, row) => total + row[reliefIndex],
    0,
  );
  return {
    count: rows.length,
    notTimelyCount: rows.length - timelyCount,
    timelyRate: (100 * timelyCount) / rows.length,
    notTimelyRate: (100 * (rows.length - timelyCount)) / rows.length,
    reliefCount,
    reliefRate: (100 * reliefCount) / rows.length,
    concentrationCount: leadingCount,
    concentrationRate: (100 * leadingCount) / rows.length,
  };
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function updateSummary(rows) {
  const summary = calculateSummary(rows);
  setText("metric-total", numberFormat.format(summary.count));
  setText("metric-exceptions", numberFormat.format(summary.notTimelyCount));
  setText("metric-relief", numberFormat.format(summary.reliefCount));
  setText(
    "metric-concentration",
    canInterpret(summary.count) ? formatPercent(summary.concentrationRate) : "—",
  );
  setText(
    "metric-total-context",
    `${numberFormat.format(summary.count)} selected source rows`,
  );
  setText(
    "metric-exceptions-context",
    canInterpret(summary.count)
      ? `${formatPercent(summary.notTimelyRate)} of selected complaints`
      : `Rate withheld below ${MIN_INTERPRETIVE_COUNT} complaints`,
  );
  setText(
    "metric-relief-context",
    canInterpret(summary.count)
      ? `${formatPercent(summary.reliefRate)} of selected complaints`
      : `Rate withheld below ${MIN_INTERPRETIVE_COUNT} complaints`,
  );

  const findingDimension = state.filters.issue === null ? "issue" : "sub_issue";
  const findingGroups = aggregate(rows, findingDimension);
  const topGroup = findingGroups[0];
  setText(
    "metric-concentration-label",
    findingDimension === "issue"
      ? "Leading issue share"
      : "Leading sub-issue share",
  );
  setText(
    "metric-concentration-context",
    topGroup
      ? `${numberFormat.format(topGroup.count)} · ${topGroup.label}`
      : "No matching complaint category",
  );
  setText(
    "metric-concentration-definition",
    findingDimension === "issue"
      ? "Largest share of published complaint volume"
      : "Largest share within the selected issue",
  );

  if (!topGroup) {
    setText("decision-finding", "No complaints match the selected filters.");
    setText(
      "decision-action",
      "Reset or broaden the filters to restore the diagnostic view.",
    );
    return;
  }

  if (!canInterpret(rows.length)) {
    setText(
      "decision-finding",
      `Small base: ${numberFormat.format(rows.length)} published complaint${rows.length === 1 ? "" : "s"} match the selected filters.`,
    );
    setText(
      "decision-action",
      `Use this as a lookup only. Rates and priority language are withheld until at least ${MIN_INTERPRETIVE_COUNT} published complaints are selected.`,
    );
    return;
  }

  if (isDefaultView()) {
    const leadingIssueRows = rowsMatchingLabel(rows, "issue", topGroup.label);
    const leadingSubIssues = aggregate(leadingIssueRows, "sub_issue").slice(0, 2);
    const leadingSubIssueCount = leadingSubIssues.reduce(
      (total, group) => total + group.count,
      0,
    );
    const excludingJanuary = rows.filter(
      (row) =>
        dictionaryValue("received_month", row[columnIndex("received_month")]) !==
        "2025-01",
    );
    const excludingJanuaryLeading =
      aggregate(excludingJanuary, "issue").find(
        (group) => group.label === topGroup.label,
      )?.count || 0;
    const excludingJanuaryShare =
      (100 * excludingJanuaryLeading) / excludingJanuary.length;
    setText(
      "decision-finding",
      `${topGroup.label} leads with ${numberFormat.format(topGroup.count)} complaints (${formatPercent((100 * topGroup.count) / rows.length)}) and remains the leading issue at ${formatPercent(excludingJanuaryShare)} after excluding January. Its two largest sub-issues total ${numberFormat.format(leadingSubIssueCount)} (${formatPercent((100 * leadingSubIssueCount) / rows.length)} of the year).`,
    );
    setText(
      "decision-action",
      "Use those account-management themes as the first discovery hypotheses. Validate them with transactions, process steps, repeat contacts, reopens, and resolution time before changing policy or staffing.",
    );
    return;
  }

  const share = (100 * topGroup.count) / rows.length;
  const findingLabel =
    findingDimension === "issue" ? "The leading issue" : "The leading sub-issue";
  setText(
    "decision-finding",
    `${findingLabel}, ${topGroup.label}, represents ${formatPercent(share)} of the selected published complaint volume (${numberFormat.format(topGroup.count)} complaints).`,
  );
  setText(
    "decision-action",
    "Treat this as an external validation lead, not a proven cause. Request the internal denominator, workflow step, case outcome, and repeat-contact evidence before choosing an intervention.",
  );
}

function chartDefaults() {
  Chart.defaults.color = palette.ink;
  Chart.defaults.font.family =
    '"Avenir Next", Avenir, "Helvetica Neue", Helvetica, sans-serif';
  Chart.defaults.font.size = 11;
  Chart.defaults.animation = false;
  Chart.defaults.responsive = true;
  Chart.defaults.maintainAspectRatio = false;
}

function baseOptions() {
  return {
    animation: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: palette.ink,
        titleFont: { weight: "600" },
        padding: 12,
        cornerRadius: 4,
      },
    },
    scales: {
      x: {
        border: { display: false },
        grid: { display: false },
        ticks: { color: palette.dark, maxRotation: 0, maxTicksLimit: 4 },
      },
      y: {
        beginAtZero: true,
        border: { display: false },
        grid: { color: palette.grid },
        ticks: { color: palette.dark },
      },
    },
  };
}

function configureMonthAxis(options, months) {
  options.scales.x.ticks = {
    autoSkip: false,
    color: palette.dark,
    maxRotation: 0,
    minRotation: 0,
    font: { size: 10 },
    callback(value, index) {
      if (months.length === 1) {
        return months[index];
      }
      return months[index]?.split(" ")[0] || "";
    },
  };
}

function upsertChart(id, type, labels, data, options) {
  const canvas = document.getElementById(id);
  if (state.charts[id]) {
    state.charts[id].data.labels = labels;
    state.charts[id].data.datasets = data;
    state.charts[id].options = options;
    state.charts[id].update("none");
    return;
  }
  state.charts[id] = new Chart(canvas, {
    type,
    data: { labels, datasets: data },
    options,
  });
}

function fillSimpleTable(tableId, rows, valueFormatter = numberFormat.format.bind(numberFormat)) {
  const body = document.querySelector(`#${tableId} tbody`);
  body.replaceChildren();
  for (const row of rows) {
    const tableRow = document.createElement("tr");
    const label = document.createElement("td");
    const value = document.createElement("td");
    label.textContent = row.label;
    value.textContent = valueFormatter(row.value);
    tableRow.append(label, value);
    body.append(tableRow);
  }
}

function updateCharts(rows) {
  const monthlyGroups = aggregateRates(rows, ["received_month"]).sort((a, b) =>
    a.labels[0].localeCompare(b.labels[0]),
  );
  const months = monthlyGroups.map((group) => formatMonth(group.labels[0]));
  const monthlyCounts = monthlyGroups.map((group) => group.count);
  const monthlyExceptionCounts = monthlyGroups.map(
    (group) => group.notTimelyCount,
  );
  const monthlyExceptionRates = monthlyGroups.map(
    (group) => group.notTimelyRate,
  );
  const medianMonthlyCount = median(monthlyCounts);
  const peakMonthlyCount = Math.max(...monthlyCounts, 0);
  const peakMonthIndex = monthlyCounts.indexOf(peakMonthlyCount);
  if (monthlyCounts.length === 1) {
    setText(
      "volume-signal",
      "One month is selected. Reset the month filter to compare the annual pattern.",
    );
  } else if (medianMonthlyCount && peakMonthlyCount > 2 * medianMonthlyCount) {
    const peakMonthValue = monthlyGroups[peakMonthIndex].labels[0];
    const peakRows = rowsMatchingLabel(rows, "received_month", peakMonthValue);
    const topPairs = aggregateRates(peakRows, ["company", "issue"]).slice(0, 2);
    const topPairCount = topPairs.reduce(
      (total, group) => total + group.count,
      0,
    );
    const nonPeakMedian = median(
      monthlyCounts.filter((_, index) => index !== peakMonthIndex),
    );
    const residual = peakMonthlyCount - topPairCount;
    const pairText = topPairs
      .map(
        (group) =>
          `${conciseCompanyLabel(group.labels[0])} + ${group.labels[1]}: ${numberFormat.format(group.count)}`,
      )
      .join("; ");
    setText(
      "volume-signal",
      `Peak ${months[peakMonthIndex]}: ${numberFormat.format(peakMonthlyCount)} (${(peakMonthlyCount / medianMonthlyCount).toFixed(1)}× annual median). Two company-issue clusters contributed ${numberFormat.format(topPairCount)} (${formatPercent((100 * topPairCount) / peakMonthlyCount)}): ${pairText}. Without them: ${numberFormat.format(residual)} (${(residual / nonPeakMedian).toFixed(2)}× the other-month median). Do not generalize this into staffing demand.`,
    );
  } else if (monthlyCounts.length) {
    setText(
      "volume-signal",
      `Peak ${months[peakMonthIndex]}: ${numberFormat.format(peakMonthlyCount)} complaints · latest ${months.at(-1)}: ${numberFormat.format(monthlyCounts.at(-1))}.`,
    );
  } else {
    setText("volume-signal", "No monthly data matches the selected filters.");
  }

  const volumeOptions = baseOptions();
  configureMonthAxis(volumeOptions, months);
  volumeOptions.scales.y.title = {
    display: true,
    text: "Complaints",
    color: palette.dark,
  };
  volumeOptions.plugins.tooltip.callbacks = {
    label(context) {
      return `${numberFormat.format(context.raw)} complaints`;
    },
  };
  upsertChart(
    "volume-chart",
    "bar",
    months,
    [
      {
        label: "Complaints",
        data: monthlyCounts,
        backgroundColor: palette.ink,
        borderWidth: 0,
        borderRadius: 2,
        barPercentage: 0.72,
        categoryPercentage: 0.82,
      },
    ],
    volumeOptions,
  );
  document
    .getElementById("volume-chart")
    .setAttribute(
      "aria-label",
      buildChartAriaLabel(
        "Monthly complaint volume",
        months.map(
          (month, index) =>
            `${month}: ${numberFormat.format(monthlyCounts[index])}`,
        ),
      ),
    );
  fillSimpleTable(
    "volume-data-table",
    months.map((label, index) => ({ label, value: monthlyCounts[index] })),
  );

  const exceptionOptions = baseOptions();
  configureMonthAxis(exceptionOptions, months);
  const interpretiveBase = canInterpret(rows.length);
  const exceptionData = interpretiveBase
    ? monthlyExceptionRates
    : monthlyExceptionCounts;
  const maximumExceptionValue = Math.max(...exceptionData, 0);
  exceptionOptions.scales.y.min = 0;
  exceptionOptions.scales.y.max = interpretiveBase
    ? Math.max(1, Math.ceil(maximumExceptionValue * 2) / 2)
    : Math.max(1, Math.ceil(maximumExceptionValue));
  exceptionOptions.scales.y.title = {
    display: true,
    text: interpretiveBase
      ? "Not-timely response (%)"
      : "Not-timely complaints",
    color: palette.dark,
  };
  exceptionOptions.scales.y.ticks.callback = (value) =>
    interpretiveBase ? `${value}%` : numberFormat.format(value);
  exceptionOptions.scales.y.ticks.stepSize = interpretiveBase ? 0.5 : 1;
  exceptionOptions.plugins.tooltip.callbacks = {
    label(context) {
      const index = context.dataIndex;
      return `${numberFormat.format(monthlyExceptionCounts[index])} not timely (${formatPercent(monthlyExceptionRates[index])})`;
    },
  };
  if (monthlyExceptionRates.length) {
    const maximumExceptionRate = Math.max(...monthlyExceptionRates);
    const maximumIndex = monthlyExceptionRates.indexOf(maximumExceptionRate);
    const totalSummary = calculateSummary(rows);
    const peakMonthValue = monthlyGroups[maximumIndex].labels[0];
    const peakExceptionRows = rowsMatchingLabel(
      rows,
      "received_month",
      peakMonthValue,
    ).filter((row) => row[columnIndex("is_timely")] === 0);
    const leadingCompany = aggregate(peakExceptionRows, "company")[0];
    const companyFilterActive = Boolean(
      document.getElementById("company-filter").value,
    );
    const companyContext =
      companyFilterActive
        ? " Company concentration is not compared while a company filter is active."
        : leadingCompany && peakExceptionRows.length
        ? ` ${conciseCompanyLabel(leadingCompany.label)} accounts for ${numberFormat.format(leadingCompany.count)} of ${numberFormat.format(peakExceptionRows.length)} (${formatPercent((100 * leadingCompany.count) / peakExceptionRows.length)}); use as a validation lead, not a company ranking.`
        : "";
    setText(
      "exception-signal",
      interpretiveBase
        ? `Peak ${months[maximumIndex]}: ${numberFormat.format(monthlyExceptionCounts[maximumIndex])} not timely (${formatPercent(maximumExceptionRate)}); selected view: ${numberFormat.format(totalSummary.notTimelyCount)} (${formatPercent(totalSummary.notTimelyRate)}).${companyContext}`
        : `Small base: showing exception counts only. Rates are withheld until at least ${MIN_INTERPRETIVE_COUNT} published complaints are selected.`,
    );
  } else {
    setText(
      "exception-signal",
      "No response-exception data matches the selected filters.",
    );
  }
  upsertChart(
    "exception-chart",
    "line",
    months,
    [
      {
        label: interpretiveBase
          ? "Not-timely response rate"
          : "Not-timely complaints",
        data: exceptionData,
        borderColor: palette.ink,
        backgroundColor: palette.white,
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0,
      },
    ],
    exceptionOptions,
  );
  document
    .getElementById("exception-chart")
    .setAttribute(
      "aria-label",
      buildChartAriaLabel(
        "Monthly not-timely response exceptions",
        months.map(
          (month, index) =>
            `${month}: ${numberFormat.format(monthlyExceptionCounts[index])} not timely, ${formatPercent(monthlyExceptionRates[index])}`,
        ),
      ),
    );
  fillSimpleTable(
    "exception-data-table",
    months.map((label, index) => ({
      label,
      value: `${numberFormat.format(monthlyExceptionCounts[index])} · ${formatPercent(monthlyExceptionRates[index])}`,
    })),
    (value) => value,
  );

  const issueDimension = state.filters.issue === null ? "issue" : "sub_issue";
  const issueGroups = aggregate(rows, issueDimension);
  const leadingIssues = issueGroups.slice(0, 5);
  const otherCount = issueGroups
    .slice(5)
    .reduce((total, group) => total + group.count, 0);
  if (otherCount) {
    leadingIssues.push({
      label:
        issueDimension === "issue"
          ? "All other issues"
          : "All other sub-issues",
      count: otherCount,
    });
  }
  const issueLabels = {
    "Problem with a lender or other company charging your account":
      "Company charged account",
    "Problem caused by your funds being low": "Low-funds problem",
    "Incorrect information on your report": "Incorrect report information",
    "Problem with a company's investigation into an existing problem":
      "Company investigation",
  };
  const issueOptions = baseOptions();
  issueOptions.indexAxis = "y";
  issueOptions.scales.y.ticks.autoSkip = false;
  setText(
    "issue-chart-title",
    issueDimension === "issue"
      ? "Leading complaint issues"
      : "Leading sub-issues",
  );
  setText(
    "issue-chart-subtitle",
    issueDimension === "issue"
      ? "Published complaint concentration in the selected view"
      : "Published complaint concentration within the selected issue",
  );
  const issueShares = leadingIssues.map((group) =>
    rows.length ? (100 * group.count) / rows.length : 0,
  );
  const issueValues = interpretiveBase
    ? issueShares
    : leadingIssues.map((group) => group.count);
  issueOptions.scales.x.beginAtZero = true;
  issueOptions.scales.x.max = Math.max(
    interpretiveBase ? 10 : 1,
    interpretiveBase
      ? Math.ceil(Math.max(...issueValues, 0) / 10) * 10
      : Math.ceil(Math.max(...issueValues, 0)),
  );
  issueOptions.scales.x.ticks.callback = (value) =>
    interpretiveBase ? `${value}%` : numberFormat.format(value);
  issueOptions.scales.x.title = {
    display: true,
    text: interpretiveBase
      ? "Share of selected complaints"
      : "Published complaints",
    color: palette.dark,
  };
  issueOptions.scales.y.ticks.callback = function issueTick(value, index) {
    const context = interpretiveBase
      ? `${numberFormat.format(leadingIssues[index].count)} · ${formatPercent(issueShares[index])}`
      : `${numberFormat.format(leadingIssues[index].count)} complaints`;
    return [...wrapChartLabel(this.getLabelForValue(value)), context];
  };
  issueOptions.plugins.tooltip.callbacks = {
    label(context) {
      const count = leadingIssues[context.dataIndex].count;
      return interpretiveBase
        ? `${numberFormat.format(count)} complaints (${formatPercent(issueShares[context.dataIndex])})`
        : `${numberFormat.format(count)} complaints; rate withheld for small base`;
    },
  };
  const topThreeIssueCount = issueGroups
    .slice(0, 3)
    .reduce((total, group) => total + group.count, 0);
  setText(
    "issue-signal",
    rows.length
      ? interpretiveBase
        ? `Top three ${issueDimension === "issue" ? "issues" : "sub-issues"}: ${numberFormat.format(topThreeIssueCount)} complaints (${formatPercent((100 * topThreeIssueCount) / rows.length)}) · remaining: ${numberFormat.format(rows.length - topThreeIssueCount)} (${formatPercent((100 * (rows.length - topThreeIssueCount)) / rows.length)}). Categories are intake labels, not validated causes.`
        : `Small base: showing complaint counts only. Shares and priority language are withheld below ${MIN_INTERPRETIVE_COUNT} complaints.`
      : "No issue data matches the selected filters.",
  );
  upsertChart(
    "issue-chart",
    "bar",
    leadingIssues.map((group) => issueLabels[group.label] || group.label),
    [
      {
        label: interpretiveBase
          ? "Share of selected complaints"
          : "Published complaints",
        data: issueValues,
        backgroundColor: palette.ink,
        borderWidth: 0,
        barPercentage: 0.72,
      },
    ],
    issueOptions,
  );
  document
    .getElementById("issue-chart")
    .setAttribute(
      "aria-label",
      buildChartAriaLabel(
        `Leading complaint ${issueDimension === "issue" ? "issues" : "sub-issues"}`,
        leadingIssues.map(
          (group) => `${group.label}: ${numberFormat.format(group.count)}`,
        ),
      ),
    );
  fillSimpleTable(
    "issue-data-table",
    leadingIssues.map((group) => ({ label: group.label, value: group.count })),
  );

  const reliefDetails = aggregateRates(rows, ["issue", "sub_issue"]).slice(0, 6);
  const reliefOptions = baseOptions();
  reliefOptions.indexAxis = "y";
  reliefOptions.scales.y.ticks.autoSkip = false;
  const reliefValues = reliefDetails.map((group) =>
    interpretiveBase ? group.reliefRate : group.reliefCount,
  );
  reliefOptions.scales.x.beginAtZero = true;
  reliefOptions.scales.x.max = interpretiveBase
    ? Math.max(5, Math.ceil(Math.max(...reliefValues, 0) / 5) * 5)
    : Math.max(1, Math.ceil(Math.max(...reliefValues, 0)));
  reliefOptions.scales.x.ticks.callback = (value) =>
    interpretiveBase ? `${value}%` : numberFormat.format(value);
  reliefOptions.scales.x.title = {
    display: true,
    text: interpretiveBase
      ? "Closed with reported relief (%)"
      : "Reported-relief complaints",
    color: palette.dark,
  };
  reliefOptions.scales.y.ticks.callback = function reliefTick(value, index) {
    const group = reliefDetails[index];
    const context = interpretiveBase
      ? `${numberFormat.format(group.reliefCount)} of ${numberFormat.format(group.count)} · ${formatPercent(group.reliefRate)}`
      : `${numberFormat.format(group.reliefCount)} of ${numberFormat.format(group.count)}`;
    return [
      ...wrapChartLabel(this.getLabelForValue(value)),
      context,
    ];
  };
  reliefOptions.plugins.tooltip.callbacks = {
    label(context) {
      const group = reliefDetails[context.dataIndex];
      return `${numberFormat.format(group.reliefCount)} of ${numberFormat.format(group.count)} closed with reported relief (${formatPercent(group.reliefRate)})`;
    },
  };
  const selectedSummary = calculateSummary(rows);
  const highestReliefDetail = [...reliefDetails].sort(
    (a, b) => b.reliefRate - a.reliefRate || b.count - a.count,
  )[0];
  setText(
    "relief-signal",
    rows.length
      ? interpretiveBase && highestReliefDetail
        ? `Selected-view baseline: ${formatPercent(selectedSummary.reliefRate)}. Highest among the six volume-selected details: ${highestReliefDetail.labels[1]} at ${formatPercent(highestReliefDetail.reliefRate)} (${numberFormat.format(highestReliefDetail.reliefCount)} of ${numberFormat.format(highestReliefDetail.count)}). This is response mix, not success or fault.`
        : `Small base: showing reported-relief counts only. Rates are withheld below ${MIN_INTERPRETIVE_COUNT} complaints.`
      : "No reported-relief data matches the selected filters.",
  );
  upsertChart(
    "relief-chart",
    "bar",
    reliefDetails.map((group) => group.labels[1]),
    [
      {
        label: interpretiveBase
          ? "Closed with reported relief"
          : "Reported-relief complaints",
        data: reliefValues,
        backgroundColor: palette.ink,
        borderWidth: 0,
        barPercentage: 0.72,
      },
    ],
    reliefOptions,
  );
  document
    .getElementById("relief-chart")
    .setAttribute(
      "aria-label",
      buildChartAriaLabel(
        "Reported-relief share in six highest-volume issue details",
        reliefDetails.map(
          (group) =>
            `${group.labels[0]} — ${group.labels[1]}: ${numberFormat.format(group.reliefCount)} of ${numberFormat.format(group.count)}, ${formatPercent(group.reliefRate)}`,
        ),
      ),
    );
  fillSimpleTable(
    "relief-data-table",
    reliefDetails.map((group) => ({
      label: `${group.labels[0]} — ${group.labels[1]}`,
      value: interpretiveBase
        ? `${numberFormat.format(group.reliefCount)} of ${numberFormat.format(group.count)} · ${formatPercent(group.reliefRate)}`
        : `${numberFormat.format(group.reliefCount)} of ${numberFormat.format(group.count)} · rate withheld`,
    })),
    (value) => value,
  );
}

function fillTable(tableId, rows) {
  const body = document.querySelector(`#${tableId} tbody`);
  body.replaceChildren();
  for (const values of rows) {
    const row = document.createElement("tr");
    for (const value of values) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    body.append(row);
  }
}

function updateTables(rows) {
  const issueDetails = aggregateRates(rows, ["issue", "sub_issue"])
    .slice(0, 10)
    .map((group) => ({ ...group, share: (100 * group.count) / rows.length }));
  fillTable(
    "issue-detail-table",
    issueDetails.map((group) => {
      const stableBase = canInterpret(group.count) && canInterpret(rows.length);
      return [
        `${group.labels[0]} — ${group.labels[1]}`,
        numberFormat.format(group.count),
        canInterpret(rows.length) ? formatPercent(group.share) : "Withheld",
        stableBase
          ? `${numberFormat.format(group.notTimelyCount)} · ${formatPercent(group.notTimelyRate)}`
          : `${numberFormat.format(group.notTimelyCount)} · rate withheld`,
        stableBase
          ? `${numberFormat.format(group.reliefCount)} · ${formatPercent(group.reliefRate)}`
          : `${numberFormat.format(group.reliefCount)} · rate withheld`,
      ];
    }),
  );

  const exceptionMonths = aggregateRates(rows, ["received_month"]).sort(
    (a, b) =>
      b.notTimelyCount - a.notTimelyCount ||
      a.labels[0].localeCompare(b.labels[0]),
  );
  fillTable(
    "exception-detail-table",
    exceptionMonths.map((group) => {
      const stableBase = canInterpret(group.count) && canInterpret(rows.length);
      return [
        formatMonth(group.labels[0]),
        numberFormat.format(group.count),
        numberFormat.format(group.notTimelyCount),
        stableBase ? formatPercent(group.notTimelyRate) : "Withheld",
        stableBase
          ? `${numberFormat.format(group.reliefCount)} · ${formatPercent(group.reliefRate)}`
          : `${numberFormat.format(group.reliefCount)} · rate withheld`,
      ];
    }),
  );
}

function updateDashboard() {
  const rows = currentRows();
  const activeFilters = Object.values(state.filters).filter(
    (value) => value !== null,
  ).length;
  setText(
    "filter-status",
    `${numberFormat.format(rows.length)} of ${numberFormat.format(state.records.length)} complaints shown${activeFilters ? ` · ${activeFilters} filter${activeFilters > 1 ? "s" : ""} active` : ""}`,
  );
  updateSummary(rows);
  updateCharts(rows);
  updateTables(rows);
}

function populateSelect(id, dictionaryName, labelFormatter = (value) => value) {
  const select = document.getElementById(id);
  state.payload.dictionaries[dictionaryName].forEach((label, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = labelFormatter(label);
    select.append(option);
  });
}

function populateRankedSelect(
  id,
  dictionaryName,
  { minimumCount = 1, showCount = false } = {},
) {
  const select = document.getElementById(id);
  const groups = aggregate(state.records, dictionaryName).filter(
    (group) => group.count >= minimumCount,
  );
  for (const group of groups) {
    const option = document.createElement("option");
    option.value = String(group.key);
    option.textContent = showCount
      ? `${group.label} (${numberFormat.format(group.count)})`
      : group.label;
    select.append(option);
  }
}

function bindFilters() {
  const bindings = [
    ["month-filter", "received_month"],
    ["subproduct-filter", "sub_product"],
    ["issue-filter", "issue"],
    ["company-filter", "company"],
  ];
  for (const [id, field] of bindings) {
    document.getElementById(id).addEventListener("change", (event) => {
      state.filters[field] =
        event.target.value === "" ? null : Number(event.target.value);
      updateDashboard();
    });
  }
  document.getElementById("filters").addEventListener("reset", () => {
    window.setTimeout(() => {
      for (const key of Object.keys(state.filters)) {
        state.filters[key] = null;
      }
      updateDashboard();
    }, 0);
  });
}

function loadDashboard() {
  try {
    if (!window.COMPLAINT_DASHBOARD_DATA) {
      throw new Error("Dashboard data asset did not load.");
    }
    state.payload = window.COMPLAINT_DASHBOARD_DATA;
    state.records = state.payload.records;
    chartDefaults();

    populateSelect("month-filter", "received_month", formatMonth);
    populateSelect("subproduct-filter", "sub_product");
    populateRankedSelect("issue-filter", "issue");
    populateRankedSelect("company-filter", "company", {
      minimumCount: 100,
      showCount: true,
    });
    bindFilters();

    setText(
      "scope-population",
      `${numberFormat.format(state.payload.meta.row_count)} complaints`,
    );
    const scopeStart = new Date(
      `${state.payload.meta.scope.date_received_min}T00:00:00Z`,
    );
    const scopeEnd = new Date(
      `${state.payload.meta.scope.date_received_max_exclusive}T00:00:00Z`,
    );
    scopeEnd.setUTCDate(scopeEnd.getUTCDate() - 1);
    const scopeYear = scopeStart.getUTCFullYear();
    setText("scope-period", `Jan–Dec ${scopeYear}`);
    setText("scope-snapshot", `${scopeYear} CFPB public-data snapshot`);
    setText(
      "freshness",
      `Static snapshot built ${new Date(state.payload.meta.generated_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })} · Source file SHA-256 ${state.payload.meta.source_sha256.slice(0, 12)}… · CC0 source`,
    );
    updateDashboard();
  } catch (error) {
    console.error(error);
    setText("filter-status", "Dashboard data could not be loaded.");
    setText(
      "decision-finding",
      "The verified dataset is unavailable in this browser session.",
    );
    setText(
      "decision-action",
      "Confirm dashboard-data.js is beside index.html, then reopen the page.",
    );
  }
}

window.addEventListener("beforeprint", () => {
  for (const chart of Object.values(state.charts)) {
    chart.resize();
  }
});

window.addEventListener("afterprint", () => {
  for (const chart of Object.values(state.charts)) {
    chart.resize();
  }
});

document.addEventListener("DOMContentLoaded", loadDashboard);
