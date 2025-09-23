import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import './Analytics.css';

function Analytics({ data, companyName }) {
  const departmentChartRef = useRef(null);
  const locationChartRef = useRef(null);
  const salaryChartRef = useRef(null);
  const chartsRef = useRef({});

  useEffect(() => {
    // Cleanup previous charts
    Object.values(chartsRef.current).forEach(chart => chart?.destroy());
    chartsRef.current = {};

    // Chart defaults
    Chart.defaults.color = 'hsl(39, 18%, 76%)';
    Chart.defaults.font.family = 'JetBrains Mono';
    Chart.defaults.font.size = 11;

    // Department Distribution Chart
    if (departmentChartRef.current && data.departments) {
      const ctx = departmentChartRef.current.getContext('2d');
      chartsRef.current.department = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data.departments).slice(0, 8),
          datasets: [{
            data: Object.values(data.departments).slice(0, 8),
            backgroundColor: [
              'hsl(17, 82%, 54%)',
              'hsl(17, 82%, 64%)',
              'hsl(39, 18%, 76%)',
              'hsl(39, 18%, 66%)',
              'hsl(34, 6%, 33%)',
              'hsl(34, 6%, 43%)',
              'hsl(30, 6%, 24%)',
              'hsl(30, 6%, 34%)'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                padding: 15,
                usePointStyle: true,
                pointStyle: 'circle',
                font: {
                  size: 11,
                  family: 'JetBrains Mono'
                }
              }
            },
            title: {
              display: true,
              text: 'DEPARTMENT DISTRIBUTION',
              font: {
                size: 14,
                family: 'JetBrains Mono',
                weight: 600
              },
              padding: 20
            }
          }
        }
      });
    }

    // Location Distribution Chart
    if (locationChartRef.current && data.locations) {
      const ctx = locationChartRef.current.getContext('2d');
      const sortedLocations = Object.entries(data.locations)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);

      chartsRef.current.location = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: sortedLocations.map(([loc]) => loc),
          datasets: [{
            label: 'Jobs',
            data: sortedLocations.map(([,count]) => count),
            backgroundColor: 'hsl(17, 82%, 54%)',
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: 'TOP LOCATIONS',
              font: {
                size: 14,
                family: 'JetBrains Mono',
                weight: 600
              },
              padding: 20
            }
          },
          scales: {
            x: {
              grid: {
                color: 'rgba(255, 255, 255, 0.05)'
              },
              ticks: {
                font: {
                  size: 10,
                  family: 'JetBrains Mono'
                }
              }
            },
            y: {
              grid: {
                color: 'rgba(255, 255, 255, 0.05)'
              },
              ticks: {
                font: {
                  size: 10,
                  family: 'JetBrains Mono'
                }
              }
            }
          }
        }
      });
    }

    // Salary Disclosure Chart
    if (salaryChartRef.current && data.salary_ranges) {
      const ctx = salaryChartRef.current.getContext('2d');
      chartsRef.current.salary = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['With Salary', 'Without Salary'],
          datasets: [{
            data: [
              data.salary_ranges.with_salary,
              data.salary_ranges.without_salary
            ],
            backgroundColor: ['hsl(17, 82%, 54%)', 'hsl(34, 6%, 33%)'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 15,
                usePointStyle: true,
                pointStyle: 'circle',
                font: {
                  size: 11,
                  family: 'JetBrains Mono'
                }
              }
            },
            title: {
              display: true,
              text: 'SALARY DISCLOSURE',
              font: {
                size: 14,
                family: 'JetBrains Mono',
                weight: 600
              },
              padding: 20
            }
          }
        }
      });
    }

    return () => {
      Object.values(chartsRef.current).forEach(chart => chart?.destroy());
    };
  }, [data]);

  const formatSalary = (amount) => {
    if (!amount) return 'N/A';
    return `$${(amount / 1000).toFixed(0)}K`;
  };

  return (
    <div className="analytics-container">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{data.total_jobs}</div>
          <div className="stat-label">Total Jobs</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.disclosure_rate?.toFixed(1)}%</div>
          <div className="stat-label">Salary Disclosure</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{Object.keys(data.departments || {}).length}</div>
          <div className="stat-label">Departments</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{Object.keys(data.locations || {}).length}</div>
          <div className="stat-label">Locations</div>
        </div>
      </div>

      {data.avg_salary && (
        <div className="salary-summary">
          <h3>Average Salary Range</h3>
          <div className="salary-range">
            <span className="salary-min">{formatSalary(data.avg_salary.min)}</span>
            <span className="salary-separator">—</span>
            <span className="salary-max">{formatSalary(data.avg_salary.max)}</span>
          </div>
        </div>
      )}

      <div className="charts-grid">
        <div className="chart-container">
          <canvas ref={departmentChartRef}></canvas>
        </div>
        <div className="chart-container">
          <canvas ref={locationChartRef}></canvas>
        </div>
        <div className="chart-container">
          <canvas ref={salaryChartRef}></canvas>
        </div>
      </div>
    </div>
  );
}

export default Analytics;