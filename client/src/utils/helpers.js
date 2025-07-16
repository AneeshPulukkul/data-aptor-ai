/**
 * Format bytes to human-readable format
 * @param {number} bytes - The size in bytes
 * @param {number} decimals - Number of decimal places to show
 * @returns {string} - Formatted string (e.g., "1.5 MB")
 */
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Format date to a readable string
 * @param {string|Date} date - The date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted date string
 */
export const formatDate = (date, options = {}) => {
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  
  const dateObj = date instanceof Date ? date : new Date(date);
  return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(dateObj);
};

/**
 * Truncate text with ellipsis
 * @param {string} text - The text to truncate
 * @param {number} length - Max length before truncation
 * @returns {string} - Truncated text
 */
export const truncateText = (text, length = 100) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

/**
 * Format a score with color code
 * @param {number} score - The score (0-100)
 * @returns {object} - Object with score and color class
 */
export const formatScore = (score) => {
  let colorClass = '';
  
  if (score >= 80) {
    colorClass = 'text-green-600';
  } else if (score >= 60) {
    colorClass = 'text-yellow-600';
  } else {
    colorClass = 'text-red-600';
  }
  
  return {
    score,
    colorClass
  };
};

/**
 * Validate file type against allowed types
 * @param {string} fileType - MIME type of the file
 * @param {Array} allowedTypes - Array of allowed MIME types
 * @returns {boolean} - Whether the file type is allowed
 */
export const isValidFileType = (fileType, allowedTypes = ['text/csv', 'application/json']) => {
  return allowedTypes.includes(fileType);
};

/**
 * Get a readable file size limit string
 * @param {number} bytes - Size limit in bytes
 * @returns {string} - Human readable size (e.g. "Max: 10 MB")
 */
export const getFileSizeLimit = (bytes = 10 * 1024 * 1024) => {
  return `Max: ${formatBytes(bytes)}`;
};
