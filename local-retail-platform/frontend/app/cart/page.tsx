/**
 * Shopping Cart Page
 * View and manage cart items
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import {
  ShoppingCart,
  Trash2,
  Plus,
  Minus,
  ArrowRight,
  Package,
  Tag,
} from 'lucide-react';
import { useCart } from '@/context/CartContext';

export default function CartPage() {
  const router = useRouter();
  const { cart, itemCount, totals, updateQuantity, removeFromCart } = useCart();
  const [updatingItems, setUpdatingItems] = useState<Set<number>>(new Set());

  const handleQuantityChange = (productId: number, newQuantity: number) => {
    setUpdatingItems((prev) => new Set(prev).add(productId));
    updateQuantity(productId, newQuantity);
    setTimeout(() => {
      setUpdatingItems((prev) => {
        const updated = new Set(prev);
        updated.delete(productId);
        return updated;
      });
    }, 300);
  };

  const handleRemove = (productId: number) => {
    if (confirm('Remove this item from your cart?')) {
      removeFromCart(productId);
    }
  };

  const handleCheckout = () => {
    router.push('/checkout');
  };

  if (itemCount === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <div className="bg-gray-100 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6">
                <ShoppingCart className="w-12 h-12 text-gray-400" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">Your Cart is Empty</h1>
              <p className="text-gray-600 mb-8">
                Looks like you haven't added anything to your cart yet.
              </p>
              <Link
                href="/products"
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
              >
                Start Shopping
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          <p className="text-gray-600 mt-1">
            {itemCount} {itemCount === 1 ? 'item' : 'items'} in your cart
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart.items.map((item) => {
              const isUpdating = updatingItems.has(item.product.id);
              const itemTotal = parseFloat(item.product.current_price) * item.quantity;

              return (
                <div
                  key={item.product.id}
                  className="bg-white rounded-lg shadow-md p-6 transition-opacity"
                  style={{ opacity: isUpdating ? 0.6 : 1 }}
                >
                  <div className="flex gap-4">
                    {/* Product Image */}
                    <div className="flex-shrink-0">
                      <div className="relative w-24 h-24 bg-gray-100 rounded-lg overflow-hidden">
                        {item.product.primary_image ? (
                          <Image
                            src={item.product.primary_image}
                            alt={item.product.name}
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Package className="w-8 h-8 text-gray-400" />
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Product Info */}
                    <div className="flex-grow">
                      <div className="flex justify-between">
                        <div>
                          <Link
                            href={`/products/${item.product.slug}`}
                            className="text-lg font-semibold text-gray-900 hover:text-blue-600"
                          >
                            {item.product.name}
                          </Link>
                          <p className="text-sm text-gray-600 mt-1">
                            {item.product.shop.name}
                          </p>
                          {item.product.category_name && (
                            <p className="text-xs text-gray-500 mt-1">
                              {item.product.category_name}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => handleRemove(item.product.id)}
                          className="text-red-600 hover:text-red-700 p-2 h-fit"
                          title="Remove from cart"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>

                      {/* Price and Quantity */}
                      <div className="flex items-center justify-between mt-4">
                        {/* Quantity Controls */}
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() =>
                              handleQuantityChange(item.product.id, item.quantity - 1)
                            }
                            disabled={item.quantity <= 1 || isUpdating}
                            className="w-8 h-8 flex items-center justify-center border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Minus className="w-4 h-4" />
                          </button>
                          <span className="w-12 text-center font-semibold">
                            {item.quantity}
                          </span>
                          <button
                            onClick={() =>
                              handleQuantityChange(item.product.id, item.quantity + 1)
                            }
                            disabled={isUpdating}
                            className="w-8 h-8 flex items-center justify-center border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Plus className="w-4 h-4" />
                          </button>
                        </div>

                        {/* Price */}
                        <div className="text-right">
                          <p className="text-sm text-gray-600">
                            €{item.product.current_price} each
                          </p>
                          <p className="text-lg font-bold text-gray-900">
                            €{itemTotal.toFixed(2)}
                          </p>
                        </div>
                      </div>

                      {/* Stock Warning */}
                      {item.product.stock_status === 'low_stock' && (
                        <div className="mt-3 flex items-center gap-2 text-orange-600 text-sm">
                          <Tag className="w-4 h-4" />
                          <span>Low stock - order soon!</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Continue Shopping */}
            <Link
              href="/products"
              className="block text-center text-blue-600 hover:text-blue-700 font-semibold py-4"
            >
              ← Continue Shopping
            </Link>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Order Summary</h2>

              {/* Summary Details */}
              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-gray-700">
                  <span>Subtotal ({itemCount} items)</span>
                  <span className="font-semibold">€{totals.subtotal.toFixed(2)}</span>
                </div>

                <div className="flex justify-between text-gray-700">
                  <span>Tax (19% VAT)</span>
                  <span className="font-semibold">€{totals.tax.toFixed(2)}</span>
                </div>

                <div className="flex justify-between text-gray-700">
                  <div>
                    <span>Shipping</span>
                    {totals.shipping === 0 && (
                      <p className="text-xs text-green-600">Free shipping!</p>
                    )}
                  </div>
                  <span className="font-semibold">
                    {totals.shipping === 0 ? 'FREE' : `€${totals.shipping.toFixed(2)}`}
                  </span>
                </div>

                {totals.subtotal < 50 && (
                  <div className="text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded p-3">
                    💡 Add €{(50 - totals.subtotal).toFixed(2)} more for free shipping!
                  </div>
                )}

                <div className="border-t pt-4">
                  <div className="flex justify-between text-lg font-bold text-gray-900">
                    <span>Total</span>
                    <span>€{totals.total.toFixed(2)}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Including VAT</p>
                </div>
              </div>

              {/* Checkout Button */}
              <button
                onClick={handleCheckout}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                Proceed to Checkout
                <ArrowRight className="w-5 h-5" />
              </button>

              {/* Security Badge */}
              <div className="mt-4 text-center text-xs text-gray-500">
                🔒 Secure checkout with encryption
              </div>

              {/* Info */}
              <div className="mt-6 pt-6 border-t space-y-3 text-sm text-gray-600">
                <div className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span>Free returns within 14 days</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span>Secure payment processing</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span>Support local merchants</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}