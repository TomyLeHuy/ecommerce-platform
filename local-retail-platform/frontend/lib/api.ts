/**
 * API Client for Local Retail Platform
 * Connects Next.js frontend to Django backend
 */

import axios, { AxiosInstance } from 'axios';

// API Base URL - Django backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage if it exists
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API Types
export interface Product {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  sku: string;
  price: string;
  sale_price: string | null;
  current_price: string;
  stock_status: 'in_stock' | 'low_stock' | 'out_of_stock';
  is_in_stock: boolean;
  primary_image: string | null;
  shop: {
    id: number;
    name: string;
    slug: string;
    merchant_name: string;
    merchant_city: string;
  };
  category_name: string;
  is_featured: boolean;
  sales_count?: number; // Added sales_count as optional
  view_count?: number; // Added view_count as optional
}

export interface ProductDetail extends Product {
  description: string;
  barcode: string;
  stock_quantity: number;
  is_low_stock: boolean;
  weight_kg: string | null;
  length_cm: string | null;
  width_cm: string | null;
  height_cm: string | null;
  is_active: boolean;
  meta_title: string;
  meta_description: string;
  view_count: number;
  sales_count: number;
  images: Array<{
    id: number;
    image: string;
    alt_text: string;
    is_primary: boolean;
  }>;
  category: {
    id: number;
    name: string;
    slug: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  parent: number | null;
  full_path: string;
  icon: string;
  is_active: boolean;
  subcategories: Category[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  product_sku: string;
  product_image: string | null;
  unit_price: string;
  quantity: number;
  line_total: string;
  tax_rate: string;
  tax_amount: string;
}

export interface Order {
  id: number;
  order_number: string;
  shop_name: string;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';
  total: string;
  item_count: number;
  ordered_at: string;
  payment_status: string;
}

export interface OrderDetail {
  id: number;
  order_number: string;
  shop: {
    id: number;
    name: string;
    slug: string;
    merchant_name: string;
    email: string;
    phone: string;
  };
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';
  fulfillment_method: 'delivery' | 'pickup';
  shipping_street_address: string;
  shipping_city: string;
  shipping_postal_code: string;
  shipping_country: string;
  subtotal: string;
  tax_amount: string;
  shipping_cost: string;
  discount_amount: string;
  tokens_used: number;
  tokens_value: string;
  total: string;
  payment_status: string;
  payment_method: string;
  customer_notes: string;
  tracking_number: string;
  tracking_url: string;
  items: OrderItem[];
  status_history: Array<{
    status: string;
    notes: string;
    changed_by: string;
    created_at: string;
  }>;
  ordered_at: string;
  confirmed_at: string | null;
  shipped_at: string | null;
  delivered_at: string | null;
  cancelled_at: string | null;
}

// API Methods
export const api = {
  // Products
  products: {
    list: async (params?: {
      page?: number;
      page_size?: number;
      search?: string;
      category?: number;
      price__gte?: number;
      price__lte?: number;
      ordering?: string;
    }): Promise<PaginatedResponse<Product>> => {
      const response = await apiClient.get('/api/products/products/', { params });
      return response.data;
    },

    get: async (slug: string): Promise<ProductDetail> => {
      const response = await apiClient.get(`/api/products/products/${slug}/`);
      return response.data;
    },

    featured: async (): Promise<Product[]> => {
      const response = await apiClient.get('/api/products/products/featured/');
      return response.data;
    },

    searchNearby: async (params: {
      latitude: number;
      longitude: number;
      radius_km?: number;
      category?: string;
      min_price?: number;
      max_price?: number;
      search?: string;
    }): Promise<PaginatedResponse<Product>> => {
      const response = await apiClient.get('/api/products/products/search_nearby/', { params });
      return response.data;
    },

    related: async (slug: string): Promise<Product[]> => {
      const response = await apiClient.get(`/api/products/products/${slug}/related/`);
      return response.data;
    },

    myProducts: async (): Promise<Product[]> => {
      const response = await apiClient.get('/api/products/products/my_products/');
      return response.data;
    },

    create: async (data: any): Promise<ProductDetail> => {
      const response = await apiClient.post('/api/products/products/', data);
      return response.data;
    },

    update: async (slug: string, data: any): Promise<ProductDetail> => {
      const response = await apiClient.patch(`/api/products/products/${slug}/`, data);
      return response.data;
    },

    delete: async (slug: string): Promise<void> => {
      await apiClient.delete(`/api/products/products/${slug}/`);
    },
  },

  // Categories
  categories: {
    list: async (): Promise<Category[]> => {
      const response = await apiClient.get('/api/products/categories/');
      return response.data;
    },

    root: async (): Promise<Category[]> => {
      const response = await apiClient.get('/api/products/categories/root/');
      return response.data;
    },

    get: async (slug: string): Promise<Category> => {
      const response = await apiClient.get(`/api/products/categories/${slug}/`);
      return response.data;
    },
  },

  // Customers
  customers: {
    register: async (data: {
      username: string;
      email: string;
      password: string;
      password_confirm: string;
      first_name?: string;
      last_name?: string;
    }) => {
      const response = await apiClient.post('/api/customers/register/', data);
      const { tokens } = response.data;
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      return response.data;
    },

    getProfile: async () => {
      const response = await apiClient.get('/api/customers/profile/me/');
      return response.data;
    },

    updateProfile: async (data: any) => {
      const response = await apiClient.patch('/api/customers/profile/me/', data);
      return response.data;
    },

    getTokenBalance: async () => {
      const response = await apiClient.get('/api/customers/profile/token_balance/');
      return response.data;
    },
  },

  // Authentication
  auth: {
    login: async (username: string, password: string) => {
      const response = await apiClient.post('/api/auth/token/', {
        username,
        password,
      });
      const { access, refresh } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      return response.data;
    },

    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },

    isAuthenticated: (): boolean => {
      if (typeof window === 'undefined') return false;
      return !!localStorage.getItem('access_token');
    },
  },

  // Orders
  orders: {
    create: async (data: {
      shipping_street_address: string;
      shipping_city: string;
      shipping_postal_code: string;
      shipping_country?: string;
      customer_notes?: string;
      items: Array<{
        product_id: number;
        quantity: number;
      }>;
    }): Promise<OrderDetail> => {
      const response = await apiClient.post('/api/orders/', data);
      return response.data;
    },

    list: async (): Promise<Order[]> => {
      const response = await apiClient.get('/api/orders/');
      return response.data;
    },

    get: async (id: number): Promise<OrderDetail> => {
      const response = await apiClient.get(`/api/orders/${id}/`);
      return response.data;
    },

    myOrders: async (): Promise<Order[]> => {
      const response = await apiClient.get('/api/orders/my_orders/');
      return response.data;
    },

    merchantOrders: async (): Promise<Order[]> => {
      const response = await apiClient.get('/api/orders/merchant_orders/');
      return response.data;
    },

    updateStatus: async (id: number, status: string, notes?: string): Promise<OrderDetail> => {
      const response = await apiClient.patch(`/api/orders/${id}/update_status/`, {
        status,
        notes,
      });
      return response.data;
    },

    updateTracking: async (id: number, tracking_number: string, tracking_url?: string): Promise<OrderDetail> => {
      const response = await apiClient.patch(`/api/orders/${id}/update_tracking/`, {
        tracking_number,
        tracking_url,
      });
      return response.data;
    },

    cancel: async (id: number, reason?: string): Promise<OrderDetail> => {
      const response = await apiClient.post(`/api/orders/${id}/cancel/`, {
        reason,
      });
      return response.data;
    },
  },
};

export default apiClient;