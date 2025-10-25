'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCart } from '@/context/CartContext';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';

export default function CheckoutPage() {
  const router = useRouter();
  const { cart, totals, clearCart } = useCart();
  const { user, isAuthenticated, isLoading } = useAuth();

  const [formData, setFormData] = useState({
    shipping_street_address: '',
    shipping_city: '',
    shipping_postal_code: '',
    shipping_country: 'DE',
    customer_notes: '',
    payment_method: 'dummy',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/customer/login?redirect=/checkout');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (user) {
      // Pre-fill shipping address from user profile
      setFormData((prev) => ({
        ...prev,
        shipping_street_address: user.shipping_street_address || '',
        shipping_city: user.shipping_city || '',
        shipping_postal_code: user.shipping_postal_code || '',
      }));
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!cart || cart.items.length === 0) {
      setError('Your cart is empty');
      return;
    }

    // Validate form
    if (!formData.shipping_street_address || !formData.shipping_city || !formData.shipping_postal_code) {
      setError('Please fill in all required shipping information');
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare order items
      const orderItems = cart.items.map((item) => ({
        product_id: item.product.id,
        quantity: item.quantity,
      }));

      // Create order
      const order = await api.orders.create({
        shipping_street_address: formData.shipping_street_address,
        shipping_city: formData.shipping_city,
        shipping_postal_code: formData.shipping_postal_code,
        shipping_country: formData.shipping_country,
        customer_notes: formData.customer_notes,
        items: orderItems,
      });

      // Clear cart
      clearCart();

      // Redirect to order confirmation
      router.push(`/customer/orders/${order.id}?confirmed=true`);
    } catch (err: any) {
      console.error('Order creation error:', err);
      if (err.response?.data) {
        // Handle validation errors
        const errors = err.response.data;
        if (typeof errors === 'object') {
          const errorMessages = Object.entries(errors)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join('\n');
          setError(errorMessages);
        } else {
          setError('Failed to create order. Please try again.');
        }
      } else {
        setError('Failed to create order. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Your cart is empty</h1>
            <p className="text-gray-600 mb-6">Add some items to your cart before checking out.</p>
            <button
              onClick={() => router.push('/products')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Browse Products
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Shipping Information */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Shipping Information</h2>

                {error && (
                  <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800 whitespace-pre-line">{error}</p>
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label htmlFor="shipping_street_address" className="block text-sm font-medium text-gray-700 mb-1">
                      Street Address *
                    </label>
                    <input
                      type="text"
                      id="shipping_street_address"
                      name="shipping_street_address"
                      value={formData.shipping_street_address}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Musterstraße 123"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="shipping_postal_code" className="block text-sm font-medium text-gray-700 mb-1">
                        Postal Code *
                      </label>
                      <input
                        type="text"
                        id="shipping_postal_code"
                        name="shipping_postal_code"
                        value={formData.shipping_postal_code}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="12345"
                      />
                    </div>

                    <div>
                      <label htmlFor="shipping_city" className="block text-sm font-medium text-gray-700 mb-1">
                        City *
                      </label>
                      <input
                        type="text"
                        id="shipping_city"
                        name="shipping_city"
                        value={formData.shipping_city}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Berlin"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="shipping_country" className="block text-sm font-medium text-gray-700 mb-1">
                      Country
                    </label>
                    <select
                      id="shipping_country"
                      name="shipping_country"
                      value={formData.shipping_country}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="DE">Germany</option>
                      <option value="AT">Austria</option>
                      <option value="CH">Switzerland</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="customer_notes" className="block text-sm font-medium text-gray-700 mb-1">
                      Delivery Instructions (Optional)
                    </label>
                    <textarea
                      id="customer_notes"
                      name="customer_notes"
                      value={formData.customer_notes}
                      onChange={handleChange}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Please leave package at the door..."
                    />
                  </div>
                </div>
              </div>

              {/* Payment Method */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment Method</h2>

                <div className="space-y-3">
                  <div className="flex items-center p-4 border-2 border-blue-500 rounded-lg bg-blue-50">
                    <input
                      type="radio"
                      id="payment_dummy"
                      name="payment_method"
                      value="dummy"
                      checked={formData.payment_method === 'dummy'}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600"
                    />
                    <label htmlFor="payment_dummy" className="ml-3 flex-1">
                      <div className="font-medium text-gray-900">Test Payment (Dummy)</div>
                      <div className="text-sm text-gray-600">
                        For testing purposes only. Order will be created without actual payment.
                      </div>
                    </label>
                  </div>

                  <div className="flex items-center p-4 border-2 border-gray-200 rounded-lg bg-gray-50 opacity-60">
                    <input type="radio" disabled className="w-4 h-4" />
                    <label className="ml-3 flex-1">
                      <div className="font-medium text-gray-900">Credit Card (Coming Soon)</div>
                      <div className="text-sm text-gray-600">Stripe integration will be added later</div>
                    </label>
                  </div>

                  <div className="flex items-center p-4 border-2 border-gray-200 rounded-lg bg-gray-50 opacity-60">
                    <input type="radio" disabled className="w-4 h-4" />
                    <label className="ml-3 flex-1">
                      <div className="font-medium text-gray-900">PayPal (Coming Soon)</div>
                      <div className="text-sm text-gray-600">PayPal integration will be added later</div>
                    </label>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? 'Processing...' : 'Place Order'}
              </button>
            </form>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Order Summary</h2>

              <div className="space-y-3 mb-4">
                {cart.items.map((item) => (
                  <div key={item.product.id} className="flex justify-between text-sm">
                    <span className="text-gray-600">
                      {item.quantity}× {item.product.name}
                    </span>
                    <span className="font-medium">
                      €{(parseFloat(item.product.current_price) * item.quantity).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>

              <div className="border-t border-gray-200 pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">€{totals.subtotal.toFixed(2)}</span>
                </div>

                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax (19% VAT)</span>
                  <span className="font-medium">€{totals.tax.toFixed(2)}</span>
                </div>

                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Shipping</span>
                  <span className="font-medium">
                    {totals.shipping === 0 ? 'FREE' : `€${totals.shipping.toFixed(2)}`}
                  </span>
                </div>

                {totals.subtotal >= 50 && (
                  <div className="text-xs text-green-600 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Free shipping unlocked!
                  </div>
                )}

                <div className="flex justify-between text-lg font-bold border-t border-gray-200 pt-2 mt-2">
                  <span>Total</span>
                  <span>€{totals.total.toFixed(2)}</span>
                </div>
              </div>

              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">Security Note</h3>
                <p className="text-xs text-gray-600">
                  This is a demo checkout. No real payment will be processed. Your order will be created for
                  testing purposes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
