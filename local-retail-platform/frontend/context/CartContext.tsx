/**
 * Shopping Cart Context
 * Global state management for shopping cart
 */

'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Product } from '@/lib/api';
import {
  Cart,
  CartItem,
  getCart,
  addToCart as addToCartUtil,
  removeFromCart as removeFromCartUtil,
  updateCartQuantity as updateCartQuantityUtil,
  clearCart as clearCartUtil,
  getCartItemCount,
  calculateTotal,
} from '@/lib/cart';

interface CartContextType {
  cart: Cart;
  itemCount: number;
  totals: {
    subtotal: number;
    tax: number;
    shipping: number;
    total: number;
  };
  addToCart: (product: Product, quantity?: number) => void;
  removeFromCart: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  clearCart: () => void;
  isInCart: (productId: number) => boolean;
  getQuantity: (productId: number) => number;
  refreshCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<Cart>({ items: [], updatedAt: new Date().toISOString() });
  const [mounted, setMounted] = useState(false);

  // Load cart on mount
  useEffect(() => {
    setCart(getCart());
    setMounted(true);
  }, []);

  // Calculate derived values
  const itemCount = getCartItemCount(cart);
  const totals = calculateTotal(cart);

  const addToCart = (product: Product, quantity: number = 1) => {
    const updatedCart = addToCartUtil(product, quantity);
    setCart(updatedCart);
  };

  const removeFromCart = (productId: number) => {
    const updatedCart = removeFromCartUtil(productId);
    setCart(updatedCart);
  };

  const updateQuantity = (productId: number, quantity: number) => {
    const updatedCart = updateCartQuantityUtil(productId, quantity);
    setCart(updatedCart);
  };

  const clearCart = () => {
    const emptyCart = clearCartUtil();
    setCart(emptyCart);
  };

  const isInCart = (productId: number): boolean => {
    return cart.items.some((item) => item.product.id === productId);
  };

  const getQuantity = (productId: number): number => {
    const item = cart.items.find((item) => item.product.id === productId);
    return item ? item.quantity : 0;
  };

  const refreshCart = () => {
    setCart(getCart());
  };

  // Don't render cart-dependent content until mounted
  // This prevents hydration mismatches
  if (!mounted) {
    return (
      <CartContext.Provider
        value={{
          cart: { items: [], updatedAt: new Date().toISOString() },
          itemCount: 0,
          totals: { subtotal: 0, tax: 0, shipping: 0, total: 0 },
          addToCart: () => {},
          removeFromCart: () => {},
          updateQuantity: () => {},
          clearCart: () => {},
          isInCart: () => false,
          getQuantity: () => 0,
          refreshCart: () => {},
        }}
      >
        {children}
      </CartContext.Provider>
    );
  }

  return (
    <CartContext.Provider
      value={{
        cart,
        itemCount,
        totals,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        isInCart,
        getQuantity,
        refreshCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}