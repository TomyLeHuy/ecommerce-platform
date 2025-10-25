/**
 * Merchant Dashboard
 * Overview and statistics for merchant users
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Package,
  TrendingUp,
  ShoppingCart,
  Euro,
  Plus,
  LogOut,
  Store,
  Edit,
} from 'lucide-react';
import { api, Product } from '@/lib/api';

export default function MerchantDashboardPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    if (!api.auth.isAuthenticated()) {
      router.push('/merchant/login');
      return;
    }

    fetchMerchantProducts();
  }, [router]);

  const fetchMerchantProducts = async () => {
    try {
      setLoading(true);
      const data = await api.products.myProducts();
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
      if ((error as any).response?.status === 401) {
        router.push('/merchant/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    api.auth.logout();
    router.push('/merchant/login');
  };

  // Calculate statistics
  const totalProducts = products.length;
  const inStockProducts = products.filter((p) => p.is_in_stock).length;
  const lowStockProducts = products.filter((p) => p.stock_status === 'low_stock').length;
  const totalSales = products.reduce((sum, p) => sum + (p.sales_count || 0), 0);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Store className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Merchant Dashboard</h1>
                <p className="text-sm text-gray-600">Manage your shop and products</p>
              </div>
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
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Statistics Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Products */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Package className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Total Products</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{totalProducts}</p>
            <p className="text-sm text-gray-600 mt-1">
              {inStockProducts} in stock
            </p>
          </div>

          {/* Low Stock */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-orange-100 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Low Stock</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{lowStockProducts}</p>
            <p className="text-sm text-gray-600 mt-1">
              {lowStockProducts > 0 ? 'Needs attention' : 'All good'}
            </p>
          </div>

          {/* Total Sales */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <ShoppingCart className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Total Sales</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{totalSales}</p>
            <p className="text-sm text-gray-600 mt-1">
              Across all products
            </p>
          </div>

          {/* Revenue (Placeholder) */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Euro className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Revenue</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">—</p>
            <p className="text-sm text-gray-600 mt-1">
              Coming soon
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/merchant/products/new')}
              className="flex items-center gap-3 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <Plus className="w-6 h-6 text-blue-600" />
              <div className="text-left">
                <p className="font-semibold text-gray-900">Add New Product</p>
                <p className="text-sm text-gray-600">Create a new listing</p>
              </div>
            </button>

            <button
              onClick={() => router.push('/merchant/products')}
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <Edit className="w-6 h-6 text-blue-600" />
              <div className="text-left">
                <p className="font-semibold text-gray-900">Manage Products</p>
                <p className="text-sm text-gray-600">Edit existing products</p>
              </div>
            </button>

            <button
              onClick={() => router.push('/merchant/orders')}
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <ShoppingCart className="w-6 h-6 text-blue-600" />
              <div className="text-left">
                <p className="font-semibold text-gray-900">View Orders</p>
                <p className="text-sm text-gray-600">Manage incoming orders</p>
              </div>
            </button>
          </div>
        </div>

        {/* Recent Products */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Your Products</h2>
            <button
              onClick={() => router.push('/merchant/products')}
              className="text-blue-600 hover:text-blue-700 font-semibold text-sm"
            >
              View All →
            </button>
          </div>

          {products.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Product</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">SKU</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Price</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Stock</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {products.slice(0, 10).map((product) => (
                    <tr key={product.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          {product.primary_image && (
                            <img
                              src={product.primary_image}
                              alt={product.name}
                              className="w-12 h-12 rounded object-cover"
                            />
                          )}
                          <div>
                            <p className="font-medium text-gray-900">{product.name}</p>
                            <p className="text-sm text-gray-600">{product.category_name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600 font-mono text-sm">{product.sku}</td>
                      <td className="py-3 px-4 font-semibold text-gray-900">
                        €{product.current_price}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                            product.stock_status === 'in_stock'
                              ? 'bg-green-100 text-green-800'
                              : product.stock_status === 'low_stock'
                              ? 'bg-orange-100 text-orange-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {product.stock_status === 'in_stock'
                            ? 'In Stock'
                            : product.stock_status === 'low_stock'
                            ? 'Low Stock'
                            : 'Out of Stock'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-600">
                          {product.sales_count || 0} sales
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No products yet</p>
              <button
                onClick={() => router.push('/merchant/products/new')}
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                <Plus className="w-5 h-5" />
                Add Your First Product
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}