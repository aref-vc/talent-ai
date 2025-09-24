import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import './Analytics.css';

function Analytics({ data, companyName }) {
  const departmentChartRef = useRef(null);
  const locationChartRef = useRef(null);
  const salaryChartRef = useRef(null);
  const salaryDistributionRef = useRef(null);
  const avgSalaryByDeptRef = useRef(null);
  const workArrangementRef = useRef(null);
  const seniorityLevelsRef = useRef(null);
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

    // NEW: Salary Range Distribution Chart
    if (salaryDistributionRef.current && data.salary_distribution) {
      const ctx = salaryDistributionRef.current.getContext('2d');
      chartsRef.current.salaryDistribution = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: Object.keys(data.salary_distribution),
          datasets: [{
            label: 'Number of Jobs',
            data: Object.values(data.salary_distribution),
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
              text: 'SALARY RANGE DISTRIBUTION',
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

    // NEW: Average Salary by Department Chart
    if (avgSalaryByDeptRef.current && data.avg_salary_by_dept) {
      const ctx = avgSalaryByDeptRef.current.getContext('2d');
      const deptData = Object.entries(data.avg_salary_by_dept)
        .filter(([, dept]) => dept.avg > 0)
        .sort(([,a], [,b]) => b.avg - a.avg)
        .slice(0, 10);

      chartsRef.current.avgSalaryByDept = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
          labels: deptData.map(([name]) => name),
          datasets: [{
            label: 'Average Salary',
            data: deptData.map(([, dept]) => dept.avg),
            backgroundColor: 'hsl(17, 82%, 54%)',
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: 'AVERAGE SALARY BY DEPARTMENT',
              font: {
                size: 14,
                family: 'JetBrains Mono',
                weight: 600
              },
              padding: 20
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `$${(context.parsed.x / 1000).toFixed(0)}K`;
                }
              }
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
                },
                callback: function(value) {
                  return `$${(value / 1000).toFixed(0)}K`;
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

    // NEW: Work Arrangement Chart (Remote/Hybrid/Onsite)
    if (workArrangementRef.current && data.work_arrangement) {
      const ctx = workArrangementRef.current.getContext('2d');
      chartsRef.current.workArrangement = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data.work_arrangement),
          datasets: [{
            data: Object.values(data.work_arrangement),
            backgroundColor: [
              'hsl(17, 82%, 54%)',  // Remote - Orange
              'hsl(39, 18%, 76%)',  // Hybrid - Beige
              'hsl(34, 6%, 33%)'    // Onsite - Dark
            ],
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
              text: 'WORK ARRANGEMENT',
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

    // NEW: Seniority Levels Chart
    if (seniorityLevelsRef.current && data.seniority_levels) {
      const ctx = seniorityLevelsRef.current.getContext('2d');
      chartsRef.current.seniorityLevels = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data.seniority_levels),
          datasets: [{
            data: Object.values(data.seniority_levels),
            backgroundColor: [
              'hsl(17, 82%, 64%)',  // Entry
              'hsl(39, 18%, 76%)',  // Mid
              'hsl(17, 82%, 54%)',  // Senior
              'hsl(34, 6%, 43%)',   // Lead
              'hsl(30, 6%, 24%)'    // Principal/Staff
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
              text: 'SENIORITY LEVELS',
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
          <div className="stat-value">{data.disclosure_rate ? `${data.disclosure_rate.toFixed(1)}%` : 'N/A'}</div>
          <div className="stat-label">Salary Disclosure Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {data.avg_salary ? `${formatSalary(data.avg_salary.min)} - ${formatSalary(data.avg_salary.max)}` : 'N/A'}
          </div>
          <div className="stat-label">Average Salary Range</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{Object.keys(data.departments || {}).length}</div>
          <div className="stat-label">Departments</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <canvas ref={departmentChartRef}></canvas>
        </div>
        <div className="chart-card">
          <canvas ref={locationChartRef}></canvas>
        </div>
        <div className="chart-card">
          <canvas ref={salaryChartRef}></canvas>
        </div>
        <div className="chart-card">
          <canvas ref={salaryDistributionRef}></canvas>
        </div>
        <div className="chart-card">
          <canvas ref={avgSalaryByDeptRef}></canvas>
        </div>
        <div className="chart-card">
          <canvas ref={workArrangementRef}></canvas>
        </div>
        <div className="chart-card">
          <canvas ref={seniorityLevelsRef}></canvas>
        </div>
      </div>

      {/* NEW: Top 10 Highest Paying Jobs Table */}
      {data.top_paying_jobs && data.top_paying_jobs.length > 0 && (
        <div className="top-jobs-section">
          <h3>🏆 TOP 10 HIGHEST PAYING JOBS</h3>
          <div className="top-jobs-table">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Job Title</th>
                  <th>Department</th>
                  <th>Location</th>
                  <th>Salary Range</th>
                </tr>
              </thead>
              <tbody>
                {data.top_paying_jobs.map((job, index) => (
                  <tr key={index}>
                    <td>{index + 1}</td>
                    <td className="job-title-cell">
                      {job.url ? (
                        <a href={job.url} target="_blank" rel="noopener noreferrer">
                          {job.title}
                        </a>
                      ) : (
                        job.title
                      )}
                    </td>
                    <td>{job.department}</td>
                    <td>{job.location}</td>
                    <td className="salary-cell">
                      {formatSalary(job.salary_min)} - {formatSalary(job.salary_max)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;