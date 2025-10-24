/**
 * Customer Dashboard
 * Overview for customer account
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ShoppingBag,
  Package,
  User,
  LogOut,
  Heart,
  Gift,
  MapPin,
  ArrowRight,
} from 'lucide-react';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

interface CustomerProfile {
  id: number;
  user: {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  total_orders: number;
  total_spent: string;
  token_balance: number;
  has_complete_profile: boolean;
}

export default function CustomerDashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout: authLogout, isLoading: authLoading } = useAuth();
  const [profile, setProfile] = useState<CustomerProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Wait for auth to load
    if (authLoading) return;

    // Check authentication
    if (!isAuthenticated) {
      router.push('/customer/login');
      return;
    }

    fetchProfile();
  }, [isAuthenticated, authLoading, router]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await api.customers.getProfile();
      setProfile(data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      if ((error as any).response?.status === 401) {
        router.push('/customer/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authLogout();
    router.push('/');
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Unable to load profile</p>
          <Link href="/" className="text-blue-600 hover:text-blue-700">
            Return to Home
          </Link>
        </div>
      </div>
    );
  }

  const displayName = profile.user.first_name
    ? `${profile.user.first_name} ${profile.user.last_name}`.trim()
    : profile.user.username;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {displayName}!
              </h1>
              <p className="text-gray-600 mt-1">Manage your orders and profile</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Profile Incomplete Warning */}
        {!profile.has_complete_profile && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-yellow-900 mb-1">
                  Complete Your Profile
                </h3>
                <p className="text-sm text-yellow-800 mb-3">
                  Add your shipping address to enable faster checkout
                </p>
                <Link
                  href="#"
                  className="inline-flex items-center gap-2 text-sm font-semibold text-yellow-900 hover:text-yellow-700"
                >
                  Update Profile
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Total Orders */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <ShoppingBag className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Total Orders</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{profile.total_orders}</p>
            <Link
              href="/customer/orders"
              className="text-sm text-blue-600 hover:text-blue-700 mt-2 inline-block"
            >
              View Orders →
            </Link>
          </div>

          {/* Total Spent */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <Package className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Total Spent</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">€{profile.total_spent}</p>
            <p className="text-sm text-gray-600 mt-2">Lifetime purchases</p>
          </div>

          {/* Loyalty Tokens */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Gift className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Loyalty Tokens</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{profile.token_balance}</p>
            <p className="text-sm text-gray-600 mt-2">= €{profile.token_balance}</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link
              href="/products"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <ShoppingBag className="w-6 h-6 text-blue-600" />
              <div>
                <p className="font-semibold text-gray-900">Continue Shopping</p>
                <p className="text-sm text-gray-600">Browse products</p>
              </div>
            </Link>

            <Link
              href="/customer/orders"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <Package className="w-6 h-6 text-blue-600" />
              <div>
                <p className="font-semibold text-gray-900">My Orders</p>
                <p className="text-sm text-gray-600">Track shipments</p>
              </div>
            </Link>

            <button
              disabled
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg opacity-50 cursor-not-allowed"
            >
              <Heart className="w-6 h-6 text-gray-400" />
              <div className="text-left">
                <p className="font-semibold text-gray-900">Favorite Shops</p>
                <p className="text-sm text-gray-600">Coming soon</p>
              </div>
            </button>
          </div>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Information</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-3 pb-4 border-b">
              <User className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Username</p>
                <p className="font-medium text-gray-900">{profile.user.username}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 pb-4 border-b">
              <User className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium text-gray-900">{profile.user.email}</p>
              </div>
            </div>
            <div className="pt-2">
              <button
                disabled
                className="text-blue-600 hover:text-blue-700 font-semibold text-sm opacity-50 cursor-not-allowed"
              >
                Edit Profile (Coming Soon)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}