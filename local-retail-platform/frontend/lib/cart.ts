/**
 * Shopping Cart Utilities
 * Handles cart operations and storage
 */

import { Product } from './api';

export interface CartItem {
  product: Product;
  quantity: number;
  addedAt: string;
}

export interface Cart {
  items: CartItem[];
  updatedAt: string;
}

const CART_STORAGE_KEY = 'shopping_cart';

/**
 * Get cart from localStorage
 */
export const getCart = (): Cart => {
  if (typeof window === 'undefined') {
    return { items: [], updatedAt: new Date().toISOString() };
  }

  try {
    const cartJson = localStorage.getItem(CART_STORAGE_KEY);
    if (cartJson) {
      return JSON.parse(cartJson);
    }
  } catch (error) {
    console.error('Error loading cart:', error);
  }

  return { items: [], updatedAt: new Date().toISOString() };
};

/**
 * Save cart to localStorage
 */
export const saveCart = (cart: Cart): void => {
  if (typeof window === 'undefined') return;

  try {
    cart.updatedAt = new Date().toISOString();
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
  } catch (error) {
    console.error('Error saving cart:', error);
  }
};

/**
 * Add product to cart
 */
export const addToCart = (product: Product, quantity: number = 1): Cart => {
  const cart = getCart();
  const existingItemIndex = cart.items.findIndex(
    (item) => item.product.id === product.id
  );

  if (existingItemIndex > -1) {
    // Update quantity if product already in cart
    cart.items[existingItemIndex].quantity += quantity;
  } else {
    // Add new item to cart
    cart.items.push({
      product,
      quantity,
      addedAt: new Date().toISOString(),
    });
  }

  saveCart(cart);
  return cart;
};

/**
 * Remove product from cart
 */
export const removeFromCart = (productId: number): Cart => {
  const cart = getCart();
  cart.items = cart.items.filter((item) => item.product.id !== productId);
  saveCart(cart);
  return cart;
};

/**
 * Update product quantity in cart
 */
export const updateCartQuantity = (productId: number, quantity: number): Cart => {
  const cart = getCart();
  const itemIndex = cart.items.findIndex((item) => item.product.id === productId);

  if (itemIndex > -1) {
    if (quantity <= 0) {
      // Remove item if quantity is 0 or negative
      cart.items.splice(itemIndex, 1);
    } else {
      cart.items[itemIndex].quantity = quantity;
    }
  }

  saveCart(cart);
  return cart;
};

/**
 * Clear entire cart
 */
export const clearCart = (): Cart => {
  const emptyCart: Cart = { items: [], updatedAt: new Date().toISOString() };
  saveCart(emptyCart);
  return emptyCart;
};

/**
 * Get cart item count
 */
export const getCartItemCount = (cart?: Cart): number => {
  const currentCart = cart || getCart();
  return currentCart.items.reduce((total, item) => total + item.quantity, 0);
};

/**
 * Calculate cart subtotal
 */
export const calculateSubtotal = (cart?: Cart): number => {
  const currentCart = cart || getCart();
  return currentCart.items.reduce((total, item) => {
    const price = parseFloat(item.product.current_price);
    return total + price * item.quantity;
  }, 0);
};

/**
 * Calculate cart tax (19% VAT for Germany)
 */
export const calculateTax = (subtotal: number, taxRate: number = 0.19): number => {
  return subtotal * taxRate;
};

/**
 * Calculate shipping cost
 */
export const calculateShipping = (subtotal: number): number => {
  // Free shipping over €50
  if (subtotal >= 50) {
    return 0;
  }
  return 4.99;
};

/**
 * Calculate cart total
 */
export const calculateTotal = (cart?: Cart): {
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
} => {
  const subtotal = calculateSubtotal(cart);
  const tax = calculateTax(subtotal);
  const shipping = calculateShipping(subtotal);
  const total = subtotal + tax + shipping;

  return {
    subtotal: Math.round(subtotal * 100) / 100,
    tax: Math.round(tax * 100) / 100,
    shipping: Math.round(shipping * 100) / 100,
    total: Math.round(total * 100) / 100,
  };
};

/**
 * Check if product is in cart
 */
export const isInCart = (productId: number, cart?: Cart): boolean => {
  const currentCart = cart || getCart();
  return currentCart.items.some((item) => item.product.id === productId);
};

/**
 * Get product quantity in cart
 */
export const getProductQuantity = (productId: number, cart?: Cart): number => {
  const currentCart = cart || getCart();
  const item = currentCart.items.find((item) => item.product.id === productId);
  return item ? item.quantity : 0;
};