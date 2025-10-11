/**
 * Product Card Component
 * Displays product information in a card layout
 */

import Image from 'next/image';
import Link from 'next/link';
import { MapPin, ShoppingCart, Tag } from 'lucide-react';
import { Product } from '@/lib/api';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const hasDiscount = product.sale_price && parseFloat(product.sale_price) < parseFloat(product.price);
  const discountPercentage = hasDiscount
    ? Math.round(((parseFloat(product.price) - parseFloat(product.sale_price!)) / parseFloat(product.price)) * 100)
    : 0;

  return (
    <Link href={`/products/${product.slug}`}>
      <div className="group bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden h-full flex flex-col">
        {/* Product Image */}
        <div className="relative w-full h-64 bg-gray-100 overflow-hidden">
          {product.primary_image ? (
            <Image
              src={product.primary_image}
              alt={product.name}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-200">
              <ShoppingCart className="w-16 h-16 text-gray-400" />
            </div>
          )}

          {/* Stock Status Badge */}
          <div className="absolute top-2 left-2">
            {product.stock_status === 'out_of_stock' && (
              <span className="bg-red-500 text-white text-xs font-semibold px-2 py-1 rounded">
                Out of Stock
              </span>
            )}
            {product.stock_status === 'low_stock' && (
              <span className="bg-orange-500 text-white text-xs font-semibold px-2 py-1 rounded">
                Low Stock
              </span>
            )}
          </div>

          {/* Discount Badge */}
          {hasDiscount && (
            <div className="absolute top-2 right-2">
              <span className="bg-red-500 text-white text-sm font-bold px-2 py-1 rounded">
                -{discountPercentage}%
              </span>
            </div>
          )}

          {/* Featured Badge */}
          {product.is_featured && (
            <div className="absolute bottom-2 left-2">
              <span className="bg-yellow-400 text-gray-900 text-xs font-semibold px-2 py-1 rounded flex items-center gap-1">
                <Tag className="w-3 h-3" />
                Featured
              </span>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="p-4 flex flex-col flex-grow">
          {/* Category */}
          {product.category_name && (
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
              {product.category_name}
            </p>
          )}

          {/* Product Name */}
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
            {product.name}
          </h3>

          {/* Short Description */}
          {product.short_description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2 flex-grow">
              {product.short_description}
            </p>
          )}

          {/* Shop Info */}
          <div className="flex items-center gap-1 text-sm text-gray-500 mb-3">
            <MapPin className="w-4 h-4" />
            <span className="truncate">
              {product.shop.name} · {product.shop.merchant_city}
            </span>
          </div>

          {/* Price */}
          <div className="flex items-baseline gap-2 mt-auto">
            <span className="text-2xl font-bold text-gray-900">
              €{product.current_price}
            </span>
            {hasDiscount && (
              <span className="text-sm text-gray-500 line-through">
                €{product.price}
              </span>
            )}
          </div>

          {/* SKU */}
          <p className="text-xs text-gray-400 mt-1">SKU: {product.sku}</p>
        </div>
      </div>
    </Link>
  );
}