import React from 'react'
import LoadingSpinner from './LoadingSpinner'

interface PageLoaderProps {
  message?: string
}

export const PageLoader: React.FC<PageLoaderProps> = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  )
}

export default PageLoader
