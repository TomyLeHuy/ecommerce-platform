/**
 * Header Component
 * Main navigation header with logo, search, and cart
 */

'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Store, Search, User, Menu, X, LogOut } from 'lucide-react';
import CartButton from './CartButton';
import { useAuth } from '@/context/AuthContext';

export default function Header() {
  const router = useRouter();
  const { user, isAuthenticated, logout, userType } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/products?search=${encodeURIComponent(searchQuery)}`);
      setSearchQuery('');
    }
  };

  return (
    <header className="bg-white border-b sticky top-0 z-50 shadow-sm">
      {/* Top Bar */}
      <div className="bg-blue-600 text-white text-sm">
        <div className="container mx-auto px-4 py-2">
          <div className="flex justify-between items-center">
            <p>✨ Support local merchants within 150km</p>
            <div className="hidden md:flex items-center gap-4">
              <Link href="/merchant/login" className="hover:text-blue-100">
                Merchant Portal
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 flex-shrink-0">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Store className="w-6 h-6 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-gray-900">Local Retail</h1>
              <p className="text-xs text-gray-600">Shop Local</p>
            </div>
          </Link>

          {/* Search Bar - Desktop */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-2xl">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search for products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </form>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {/* User Menu - Desktop */}
            <div className="hidden md:block relative">
              {isAuthenticated && user ? (
                <div>
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <User className="w-5 h-5" />
                    <span className="text-sm font-medium">{user.username}</span>
                  </button>

                  {/* Dropdown Menu */}
                  {userMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                      <Link
                        href={userType === 'merchant' ? '/merchant/dashboard' : '/customer/dashboard'}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        Dashboard
                      </Link>
                      <Link
                        href={userType === 'merchant' ? '/merchant/orders' : '/customer/orders'}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        {userType === 'merchant' ? 'Orders' : 'My Orders'}
                      </Link>
                      {userType === 'merchant' && (
                        <Link
                          href="/merchant/products"
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          Products
                        </Link>
                      )}
                      <hr className="my-2" />
                      <button
                        onClick={() => {
                          logout();
                          setUserMenuOpen(false);
                          router.push('/');
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                      >
                        <LogOut className="w-4 h-4" />
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <Link
                  href="/customer/login"
                  className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <User className="w-5 h-5" />
                  <span className="text-sm font-medium">Login</span>
                </Link>
              )}
            </div>

            {/* Cart Button - Only show for customers or non-authenticated users */}
            {userType !== 'merchant' && <CartButton />}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Search Bar - Mobile */}
        <form onSubmit={handleSearch} className="md:hidden mt-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </form>
      </div>

      {/* Navigation Links - Desktop - Only show for non-merchant users */}
      {userType !== 'merchant' && (
        <nav className="hidden md:block border-t">
          <div className="container mx-auto px-4">
            <ul className="flex items-center gap-8 py-3">
              <li>
                <Link
                  href="/products"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  All Products
                </Link>
              </li>
              <li>
                <Link
                  href="/products?featured=true"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Featured
                </Link>
              </li>
              <li>
                <Link
                  href="/customer/orders"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  My Orders
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      )}

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t bg-white">
          <div className="container mx-auto px-4 py-4">
            <nav className="space-y-2">
              {userType === 'merchant' ? (
                <>
                  {/* Merchant-specific mobile menu */}
                  <Link
                    href="/merchant/dashboard"
                    className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/merchant/products"
                    className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Products
                  </Link>
                  <Link
                    href="/merchant/orders"
                    className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Orders
                  </Link>
                </>
              ) : (
                <>
                  {/* Customer-specific mobile menu */}
                  <Link
                    href="/products"
                    className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    All Products
                  </Link>
                  <Link
                    href="/products?featured=true"
                    className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Featured
                  </Link>
                  <Link
                    href="/customer/orders"
                    className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    My Orders
                  </Link>
                  {!isAuthenticated && (
                    <Link
                      href="/customer/login"
                      className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Account
                    </Link>
                  )}
                  <Link
                    href="/merchant/login"
                    className="block px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Merchant Portal
                  </Link>
                </>
              )}
            </nav>
          </div>
        </div>
      )}
    </header>
  );
}