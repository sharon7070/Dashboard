(() => {
  (function () {
    "use strict";
    if ($(".report-bar-chart-1").length) {
      let a = $(".report-bar-chart-1")[0].getContext("2d"),
        e = new Chart(a, {
          type: "bar",
          data: {
            labels: [
              "Jan",
              "Feb",
              "Mar",
              "Apr",
              "May",
              "Jun",
              "Jul",
              "Aug",
              "Sep",
              "Oct",
              "Nov",
              "Dec",
            ],
            datasets: [
              {
                label: "Html Template",
                barThickness: 8,
                maxBarThickness: 6,
                data: [60, 150, 30, 200, 180, 50, 180, 120, 230, 180, 250, 270],
                backgroundColor: () => getColor("primary", 0.9),
              },
              {
                label: "VueJs Template",
                barThickness: 8,
                maxBarThickness: 6,
                data: [50, 135, 40, 180, 190, 60, 150, 90, 250, 170, 240, 250],
                backgroundColor: () =>
                  $("html").hasClass("dark")
                    ? getColor("darkmode.400")
                    : getColor("slate.300"),
              },
            ],
          },
          options: {
            maintainAspectRatio: !1,
            plugins: { legend: { display: !1 } },
            scales: {
              x: {
                ticks: {
                  font: { size: 11 },
                  color: getColor("slate.500", 0.8),
                },
                grid: { display: !1 },
                border: { display: !1 },
              },
              y: {
                ticks: { display: !1 },
                grid: {
                  color: () =>
                    $("html").hasClass("dark")
                      ? getColor("darkmode.300", 0.8)
                      : getColor("slate.300"),
                },
                border: { dash: [2, 2], display: !1 },
              },
            },
          },
        });
      helper.watchClassNameChanges($("html")[0], (s) => {
        e.update();
      });
    }
  })();
})();
