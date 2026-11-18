import React, { Suspense, lazy } from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

// ── Lazy page imports ──────────────────────────────────────────────────────────
const HomePage      = lazy(() => import('./pages/HomePage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const DetectPage    = lazy(() => import('./pages/DetectPage'))
const MapPage       = lazy(() => import('./pages/MapPage'))
const ReportsPage   = lazy(() => import('./pages/ReportsPage'))
const HistoryPage   = lazy(() => import('./pages/HistoryPage'))
const AboutPage     = lazy(() => import('./pages/AboutPage'))
const LoginPage     = lazy(() => import('./pages/LoginPage'))
const RegisterPage  = lazy(() => import('./pages/RegisterPage'))

// ── Layout components ─────────────────────────────────────────────────────────
const Navbar = lazy(() => import('./components/Navbar'))
const Footer = lazy(() => import('./components/Footer'))

// ── Loading fallback ──────────────────────────────────────────────────────────
function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <motion.div
        className="flex flex-col items-center gap-4"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Loading RoadSense…</p>
      </motion.div>
    </div>
  )
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
        <Suspense fallback={null}>
          <Navbar />
        </Suspense>

        <main className="flex-1">
          <Suspense fallback={<PageLoader />}>
            <AnimatePresence mode="wait">
              <Routes>
                {/* Public Routes */}
                <Route path="/"          element={<HomePage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/map"       element={<MapPage />} />
                <Route path="/about"     element={<AboutPage />} />
                <Route path="/login"     element={<LoginPage />} />
                <Route path="/register"  element={<RegisterPage />} />

                {/* JWT Protected Routes */}
                <Route
                  path="/detect"
                  element={
                    <ProtectedRoute>
                      <DetectPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/reports"
                  element={
                    <ProtectedRoute>
                      <ReportsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/history"
                  element={
                    <ProtectedRoute>
                      <HistoryPage />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </AnimatePresence>
          </Suspense>
        </main>

        <Suspense fallback={null}>
          <Footer />
        </Suspense>
      </div>
    </AuthProvider>
  )
}
