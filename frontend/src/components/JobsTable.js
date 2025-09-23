import React, { useState } from 'react';
import './JobsTable.css';

function JobsTable({ jobs }) {
  const [filter, setFilter] = useState('');
  const [sortField, setSortField] = useState('title');
  const [sortOrder, setSortOrder] = useState('asc');

  const filteredJobs = jobs.filter(job => {
    const searchTerm = filter.toLowerCase();
    return (
      job.title.toLowerCase().includes(searchTerm) ||
      job.location.toLowerCase().includes(searchTerm) ||
      job.department.toLowerCase().includes(searchTerm)
    );
  });

  const sortedJobs = [...filteredJobs].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];

    if (sortField === 'salary') {
      aVal = a.salary?.min || 0;
      bVal = b.salary?.min || 0;
    }

    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }

    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const formatSalary = (salary) => {
    if (!salary) return '-';
    const min = (salary.min / 1000).toFixed(0);
    const max = (salary.max / 1000).toFixed(0);
    return `$${min}K - $${max}K`;
  };

  return (
    <div className="jobs-table-container">
      <div className="table-controls">
        <input
          type="text"
          placeholder="Filter jobs..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="filter-input"
        />
        <span className="job-count">
          Showing {sortedJobs.length} of {jobs.length} jobs
        </span>
      </div>

      <div className="table-wrapper">
        <table className="jobs-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('title')}>
                Title {sortField === 'title' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('department')}>
                Department {sortField === 'department' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('location')}>
                Location {sortField === 'location' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('salary')}>
                Salary {sortField === 'salary' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {sortedJobs.map((job, index) => (
              <tr key={index}>
                <td className="job-title">{job.title}</td>
                <td>{job.department}</td>
                <td>{job.location}</td>
                <td className={job.salary ? 'has-salary' : 'no-salary'}>
                  {formatSalary(job.salary)}
                </td>
                <td>
                  {job.url && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="view-btn"
                    >
                      View →
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default JobsTable;