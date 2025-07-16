import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import logo from '../assets/logo.svg';

const Navbar = ({ isLoggedIn, setIsLoggedIn }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    setIsLoggedIn(false);
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              {/* Replace with actual logo */}
              <img className="h-10 w-auto" src={logo} alt="DataAptor AI Logo" />
              <span className="ml-2 text-xl font-bold text-primary-700">DataAptor AI</span>
            </Link>
            <div className="ml-10 flex items-baseline space-x-4">
              <Link
                to="/"
                className="text-gray-600 hover:text-primary-700 px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link
                to="/upload"
                className="text-gray-600 hover:text-primary-700 px-3 py-2 rounded-md text-sm font-medium"
              >
                Upload
              </Link>
            </div>
          </div>
          <div className="block">
            <div className="ml-4 flex items-center md:ml-6">
              {isLoggedIn ? (
                <button
                  onClick={handleLogout}
                  className="text-gray-600 hover:text-primary-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Logout
                </button>
              ) : (
                <button
                  onClick={() => setIsLoggedIn(true)}
                  className="text-gray-600 hover:text-primary-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Login
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
