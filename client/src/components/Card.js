import React from 'react';

const Card = ({ title, children, className = '', action }) => {
  return (
    <div className={`bg-white shadow-md rounded-lg overflow-hidden ${className}`}>
      {title && (
        <div className="flex justify-between items-center px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
          {action}
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
};

export default Card;
