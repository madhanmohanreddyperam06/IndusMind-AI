import { Link } from 'react-router-dom';

export function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-100 py-12 md:py-16">
      <div className="max-w-[1400px] mx-auto px-4 md:px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="mb-6 md:mb-0">
            <h3 className="text-lg md:text-xl font-semibold text-white">IndusMind AI</h3>
            <p className="text-gray-400 text-xs md:text-sm mt-2">Industrial Knowledge Intelligence Platform</p>
          </div>
          <div className="flex space-x-4 md:space-x-8">
            <Link to="#" className="text-gray-400 hover:text-white text-xs md:text-sm transition-colors">Privacy</Link>
            <Link to="#" className="text-gray-400 hover:text-white text-xs md:text-sm transition-colors">Terms</Link>
            <Link to="#" className="text-gray-400 hover:text-white text-xs md:text-sm transition-colors">Contact</Link>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-8 md:mt-12 pt-6 md:pt-8 text-center text-xs md:text-sm text-gray-400">
          <p>&copy; 2024 IndusMind AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
