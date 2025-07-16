import React from 'react';

const NotFound = () => {
  return (
    <div className="text-center py-16">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
      <h2 className="text-2xl font-semibold mb-6">Page Not Found</h2>
      <p className="text-gray-600 mb-8">
        The page you are looking for does not exist or has been moved.
      </p>
      <a href="/" className="btn-primary">
        Return to Dashboard
      </a>
    </div>
  );
};

export default NotFound;
