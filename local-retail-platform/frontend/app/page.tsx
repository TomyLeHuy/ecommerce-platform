/**
 * Homepage - Local Retail Platform
 * Displays featured products and browse options
 */

'use client';

import { useEffect, useState } from 'react';
import { Store, Search, MapPin, TrendingUp } from 'lucide-react';
import { api, Product } from '@/lib/api';
import ProductCard from '@/components/ProductCard';

export default function HomePage() {
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        
        // Fetch featured products
        const featured = await api.products.featured();
        setFeaturedProducts(featured);

        // Fetch recent products
        const response = await api.products.list({ page_size: 12, ordering: '-created_at' });
        setAllProducts(response.results);
      } catch (err) {
        console.error('Error fetching products:', err);
        setError('Failed to load products. Please ensure the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading products...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Products</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <p className="text-sm text-gray-600">
              Make sure your Django backend is running at{' '}
              <code className="bg-gray-100 px-2 py-1 rounded">http://127.0.0.1:8000</code>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <Store className="w-8 h-8" />
              <h1 className="text-4xl md:text-5xl font-bold">
                Local Retail Platform
              </h1>
            </div>
            <p className="text-xl md:text-2xl text-blue-100 mb-8">
              Discover products from local merchants within 150km
            </p>
            
            {/* Search Bar Placeholder */}
            <div className="bg-white rounded-lg shadow-lg p-2 flex items-center gap-2">
              <Search className="w-5 h-5 text-gray-400 ml-2" />
              <input
                type="text"
                placeholder="Search for products..."
                className="flex-1 px-2 py-3 text-gray-900 focus:outline-none"
              />
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-semibold transition-colors">
                Search
              </button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-4 mt-8">
              <div className="text-center">
                <p className="text-3xl font-bold">{allProducts.length}+</p>
                <p className="text-blue-200 text-sm">Products</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold">150km</p>
                <p className="text-blue-200 text-sm">Search Radius</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold">Local</p>
                <p className="text-blue-200 text-sm">Merchants</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Local Discovery</h3>
              <p className="text-gray-600">
                Find products from merchants in your area with geo-based search
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Support Local Business</h3>
              <p className="text-gray-600">
                Help small retailers compete in the digital marketplace
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Store className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Loyalty Rewards</h3>
              <p className="text-gray-600">
                Earn tokens for every €100 spent, redeemable on future purchases
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      {featuredProducts.length > 0 && (
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-3xl font-bold text-gray-900">Featured Products</h2>
              <a href="/products" className="text-blue-600 hover:text-blue-700 font-semibold">
                View All →
              </a>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredProducts.slice(0, 4).map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* All Products Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Recent Products</h2>
          {allProducts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {allProducts.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Store className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No products available yet.</p>
              <p className="text-gray-400 text-sm mt-2">
                Add products through the admin panel to see them here.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}