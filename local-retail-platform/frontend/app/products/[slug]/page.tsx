/**
 * Product Detail Page
 * Shows full product information, images, and related products
 */

'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import {
  ShoppingCart,
  MapPin,
  Package,
  TrendingUp,
  Store,
  ArrowLeft,
  Check,
  X,
  AlertCircle,
} from 'lucide-react';
import { api, ProductDetail, Product } from '@/lib/api';
import ProductCard from '@/components/ProductCard';
import { useCart } from '@/context/CartContext';

export default function ProductDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const { addToCart, isInCart } = useCart();

  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [relatedProducts, setRelatedProducts] = useState<Product[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addingToCart, setAddingToCart] = useState(false);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        const productData = await api.products.get(slug);
        setProduct(productData);

        // Set primary image or first available image
        const primaryImg = productData.images.find((img) => img.is_primary);
        if (primaryImg) {
          setSelectedImage(primaryImg.image);
        } else if (productData.images.length > 0) {
          setSelectedImage(productData.images[0].image);
        }

        // Fetch related products
        const related = await api.products.related(slug);
        setRelatedProducts(related);
      } catch (err) {
        console.error('Error fetching product:', err);
        setError('Product not found');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [slug]);

  const handleAddToCart = () => {
    if (!product) return;
    setAddingToCart(true);
    addToCart(product, 1);
    setTimeout(() => setAddingToCart(false), 1000);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading product...</p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Product Not Found</h2>
          <p className="text-gray-600 mb-4">The product you're looking for doesn't exist.</p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  const hasDiscount =
    product.sale_price && parseFloat(product.sale_price) < parseFloat(product.price);
  const discountPercentage = hasDiscount
    ? Math.round(
        ((parseFloat(product.price) - parseFloat(product.sale_price!)) /
          parseFloat(product.price)) *
          100
      )
    : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Link href="/" className="hover:text-blue-600">
              Home
            </Link>
            <span>/</span>
            <Link href="/products" className="hover:text-blue-600">
              Products
            </Link>
            <span>/</span>
            <span className="text-gray-900">{product.name}</span>
          </div>
        </div>
      </div>

      {/* Product Detail */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Image Gallery */}
          <div>
            {/* Main Image */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden mb-4">
              <div className="relative w-full h-96 bg-gray-100">
                {selectedImage ? (
                  <Image
                    src={selectedImage}
                    alt={product.name}
                    fill
                    className="object-contain"
                    priority
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Package className="w-24 h-24 text-gray-300" />
                  </div>
                )}
              </div>
            </div>

            {/* Thumbnail Gallery */}
            {product.images.length > 1 && (
              <div className="grid grid-cols-4 gap-2">
                {product.images.map((image) => (
                  <button
                    key={image.id}
                    onClick={() => setSelectedImage(image.image)}
                    className={`relative h-24 bg-white rounded-lg overflow-hidden border-2 transition-all ${
                      selectedImage === image.image
                        ? 'border-blue-600'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Image
                      src={image.image}
                      alt={image.alt_text || product.name}
                      fill
                      className="object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Product Information */}
          <div>
            {/* Category */}
            {product.category && (
              <p className="text-sm text-gray-500 uppercase tracking-wide mb-2">
                {product.category.name}
              </p>
            )}

            {/* Product Name */}
            <h1 className="text-4xl font-bold text-gray-900 mb-4">{product.name}</h1>

            {/* Price */}
            <div className="flex items-baseline gap-4 mb-6">
              <span className="text-4xl font-bold text-gray-900">
                €{product.current_price}
              </span>
              {hasDiscount && (
                <>
                  <span className="text-2xl text-gray-500 line-through">
                    €{product.price}
                  </span>
                  <span className="bg-red-500 text-white text-sm font-bold px-3 py-1 rounded">
                    Save {discountPercentage}%
                  </span>
                </>
              )}
            </div>

            {/* Stock Status */}
            <div className="mb-6">
              {product.stock_status === 'in_stock' && (
                <div className="flex items-center gap-2 text-green-600">
                  <Check className="w-5 h-5" />
                  <span className="font-semibold">In Stock ({product.stock_quantity} available)</span>
                </div>
              )}
              {product.stock_status === 'low_stock' && (
                <div className="flex items-center gap-2 text-orange-600">
                  <AlertCircle className="w-5 h-5" />
                  <span className="font-semibold">
                    Low Stock (Only {product.stock_quantity} left!)
                  </span>
                </div>
              )}
              {product.stock_status === 'out_of_stock' && (
                <div className="flex items-center gap-2 text-red-600">
                  <X className="w-5 h-5" />
                  <span className="font-semibold">Out of Stock</span>
                </div>
              )}
            </div>

            {/* Short Description */}
            {product.short_description && (
              <p className="text-lg text-gray-600 mb-6">{product.short_description}</p>
            )}

            {/* Add to Cart */}
            <button
              onClick={handleAddToCart}
              disabled={!product.is_in_stock || addingToCart}
              className={`w-full py-4 px-6 rounded-lg font-semibold text-lg flex items-center justify-center gap-2 transition-colors ${
                product.is_in_stock
                  ? 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-blue-400'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              <ShoppingCart className="w-6 h-6" />
              {addingToCart ? 'Added!' : product.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
            </button>

            {/* Shop Information */}
            <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
              <div className="flex items-start gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Store className="w-8 h-8 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {product.shop.name}
                  </h3>
                  <p className="text-gray-600 mb-2">{product.shop.merchant_name}</p>
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <MapPin className="w-4 h-4" />
                    <span>{product.shop.merchant_city}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Product Stats */}
            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                <TrendingUp className="w-6 h-6 text-green-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">{product.sales_count || 0}</p>
                <p className="text-sm text-gray-600">Sales</p>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                <Package className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600 font-mono">{product.sku}</p>
                <p className="text-sm text-gray-600">SKU</p>
              </div>
            </div>
          </div>
        </div>

        {/* Product Description */}
        <div className="mt-12 bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Product Description</h2>
          <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
            {product.description}
          </div>

          {/* Product Specifications */}
          {(product.weight_kg || product.length_cm || product.width_cm || product.height_cm) && (
            <div className="mt-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Specifications</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {product.weight_kg && (
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Weight</span>
                    <span className="font-semibold">{product.weight_kg} kg</span>
                  </div>
                )}
                {product.length_cm && (
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Length</span>
                    <span className="font-semibold">{product.length_cm} cm</span>
                  </div>
                )}
                {product.width_cm && (
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Width</span>
                    <span className="font-semibold">{product.width_cm} cm</span>
                  </div>
                )}
                {product.height_cm && (
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Height</span>
                    <span className="font-semibold">{product.height_cm} cm</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Related Products */}
        {relatedProducts.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Products</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {relatedProducts.map((relatedProduct) => (
                <ProductCard key={relatedProduct.id} product={relatedProduct} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}