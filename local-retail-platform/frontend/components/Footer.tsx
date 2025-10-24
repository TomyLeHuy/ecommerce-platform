/**
 * Footer Component
 * Site footer with links and information
 */

import Link from 'next/link';
import { Store, Mail, MapPin, Phone } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      {/* Main Footer */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Store className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-white font-bold text-lg">Local Retail</h3>
                <p className="text-xs text-gray-400">Shop Local</p>
              </div>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Supporting local merchants and bringing communities together through digital commerce.
            </p>
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="w-4 h-4" />
              <span>Within 150km radius</span>
            </div>
          </div>

          {/* Shop */}
          <div>
            <h4 className="text-white font-semibold mb-4">Shop</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/products" className="hover:text-white transition-colors">
                  All Products
                </Link>
              </li>
              <li>
                <Link href="/products?featured=true" className="hover:text-white transition-colors">
                  Featured Products
                </Link>
              </li>
              <li>
                <Link href="/products" className="hover:text-white transition-colors">
                  Categories
                </Link>
              </li>
              <li>
                <Link href="/cart" className="hover:text-white transition-colors">
                  Shopping Cart
                </Link>
              </li>
            </ul>
          </div>

          {/* Customer */}
          <div>
            <h4 className="text-white font-semibold mb-4">Customer</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/customer/login" className="hover:text-white transition-colors">
                  My Account
                </Link>
              </li>
              <li>
                <Link href="/customer/orders" className="hover:text-white transition-colors">
                  Order History
                </Link>
              </li>
              <li>
                <Link href="/customer/register" className="hover:text-white transition-colors">
                  Create Account
                </Link>
              </li>
              <li>
                <Link href="/customer/dashboard" className="hover:text-white transition-colors">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>

          {/* Merchants */}
          <div>
            <h4 className="text-white font-semibold mb-4">For Merchants</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/merchant/login" className="hover:text-white transition-colors">
                  Merchant Login
                </Link>
              </li>
              <li>
                <Link href="/merchant/dashboard" className="hover:text-white transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/merchant/products" className="hover:text-white transition-colors">
                  Manage Products
                </Link>
              </li>
              <li>
                <a href="http://127.0.0.1:8000/admin/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">
                  Django Admin
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-800">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-400">
            <p>
              © {currentYear} Local Retail Platform. All rights reserved.
            </p>
            <div className="flex gap-6">
              <Link href="#" className="hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link href="#" className="hover:text-white transition-colors">
                Terms of Service
              </Link>
              <Link href="#" className="hover:text-white transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}