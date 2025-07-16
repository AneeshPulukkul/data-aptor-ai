import React from 'react';

const LoadingSpinner = ({ size = 'md', message = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
    xl: 'h-24 w-24'
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`animate-spin rounded-full ${sizeClasses[size]} border-t-2 border-b-2 border-primary-600`}></div>
      {message && <p className="mt-4 text-gray-600">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
