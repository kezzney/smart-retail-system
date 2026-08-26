/**
 * Shelf Monitoring & Stock Level Detection Page
 *
 * Implements Stage 5 of the Smart Retail Intelligence System:
 * - Real-time retail display shelf monitoring via YOLO object detection
 * - Visual bounding box overlay and shelf tier gap identification
 * - Out-of-stock estimation and front-facing density analytics
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  getVisionSamples,
  getSampleImageUrl,
  analyzeShelf,
} from '../services/api';
import type {
  SampleImageItem,
  ShelfAnalysisResponse,
  BoundingBox,
  ShelfGap,
} from '../types';

const STATUS_CONFIG: Record<
  string,
  { label: string; bg: string; text: string; border: string; symbol: string }
> = {
  OPTIMAL: {
    label: 'Optimal Stock',
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    border: 'border-emerald-500/30',
    symbol: '🟢',
  },
  MODERATE: {
    label: 'Moderate Fill',
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    border: 'border-blue-500/30',
    symbol: '🔵',
  },
  LOW_STOCK: {
    label: 'Low Stock Alert',
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    symbol: '🟡',
  },
  CRITICAL_STOCKOUT: {
    label: 'Critical Stockout',
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500/30',
    symbol: '🔴',
  },
};

export const ShelfMonitoringPage: React.FC = () => {
  const [samples, setSamples] = useState<SampleImageItem[]>([]);
  const [selectedSampleId, setSelectedSampleId] = useState<string>('sample_01');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedPreviewUrl, setUploadedPreviewUrl] = useState<string | null>(null);

  const [confidence, setConfidence] = useState<number>(0.25);
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [showGaps, setShowGaps] = useState<boolean>(true);

  const [analysis, setAnalysis] = useState<ShelfAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [hoveredBox, setHoveredBox] = useState<BoundingBox | null>(null);
  const [hoveredGap, setHoveredGap] = useState<ShelfGap | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Load sample image presets on mount
  useEffect(() => {
    let isMounted = true;
    async function loadSamples() {
      try {
        const res = await getVisionSamples();
        if (isMounted && res.samples.length > 0) {
          setSamples(res.samples);
          setSelectedSampleId(res.samples[0].sample_id);
        }
      } catch (err) {
        console.error('Failed to load vision sample images:', err);
      }
    }
    loadSamples();
    return () => {
      isMounted = false;
    };
  }, []);

  const [triggerIndex, setTriggerIndex] = useState<number>(0);

  // Trigger shelf analysis
  const runAnalysis = () => {
    setTriggerIndex((prev) => prev + 1);
  };

  // Run analysis when sample changes, file changes, or triggerIndex increments
  useEffect(() => {
    let isMounted = true;

    async function performAnalysis() {
      if (!selectedSampleId && !uploadedFile) return;

      try {
        setLoading(true);
        setError(null);

        let result: ShelfAnalysisResponse;
        if (uploadedFile) {
          result = await analyzeShelf({
            file: uploadedFile,
            conf: confidence,
          });
        } else {
          result = await analyzeShelf({
            sampleId: selectedSampleId,
            conf: confidence,
          });
        }

        if (isMounted) {
          setAnalysis(result);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : 'Failed to analyze shelf image';
          setError(msg);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    performAnalysis();

    return () => {
      isMounted = false;
    };
  }, [selectedSampleId, uploadedFile, triggerIndex, confidence]);


  // Handle custom image file upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      const objectUrl = URL.createObjectURL(file);
      setUploadedPreviewUrl(objectUrl);
      setAnalysis(null);
    }
  };

  // Reset to preset sample
  const handleSelectSample = (sampleId: string) => {
    if (uploadedPreviewUrl) {
      URL.revokeObjectURL(uploadedPreviewUrl);
    }
    setUploadedFile(null);
    setUploadedPreviewUrl(null);
    setSelectedSampleId(sampleId);
  };

  // Current image source URL
  const currentImageUrl = useMemo(() => {
    if (uploadedPreviewUrl) return uploadedPreviewUrl;
    if (selectedSampleId) return getSampleImageUrl(selectedSampleId);
    return null;
  }, [uploadedPreviewUrl, selectedSampleId]);

  const currentStatus = analysis ? STATUS_CONFIG[analysis.stock_status] || STATUS_CONFIG.MODERATE : null;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              Shelf Monitoring & Stock Level Detection
            </h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Stage 5 Active
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            YOLO object detection for product presence auditing, shelf occupancy, and empty slot detection.
          </p>
        </div>

        <button
          onClick={runAnalysis}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition disabled:opacity-50 shadow-sm"
        >
          <span className={loading ? 'animate-spin inline-block' : ''}>🔄</span>
          {loading ? 'Analyzing Shelf...' : 'Run Vision Inference'}
        </button>
      </div>

      {/* KPI Cards Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 text-lg">
            📦
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">
              {analysis ? analysis.total_detected_products : '—'}
            </div>
            <div className="text-xs text-slate-400">Detected Facings</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-lg">
            📊
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-400">
              {analysis ? `${analysis.estimated_occupancy_pct}%` : '—'}
            </div>
            <div className="text-xs text-slate-400">Estimated Occupancy</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-lg">
            🏬
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">
              {analysis ? analysis.estimated_shelf_capacity : '—'}
            </div>
            <div className="text-xs text-slate-400">Estimated Capacity</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 text-lg">
            ⚠️
          </div>
          <div>
            <div className="text-2xl font-bold text-amber-400">
              {analysis ? analysis.detected_gaps.length : '—'}
            </div>
            <div className="text-xs text-slate-400">Detected Empty Gaps</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20 text-lg">
            ⚡
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">
              {analysis ? `${analysis.inference_time_ms} ms` : '—'}
            </div>
            <div className="text-xs text-slate-400">CPU Latency</div>
          </div>
        </div>
      </div>

      {/* Main Grid: Visualizer Canvas (Left/Top) + Controls & Alerts (Right/Bottom) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visualizer Canvas Card */}
        <div className="lg:col-span-12 xl:col-span-8 bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 flex flex-col">
          {/* Top Bar of Canvas */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-700/60">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Shelf Vision View
              </span>
              {currentStatus && (
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${currentStatus.bg} ${currentStatus.text} ${currentStatus.border}`}
                >
                  <span>{currentStatus.symbol}</span>
                  {currentStatus.label}
                </span>
              )}
            </div>

            {/* Overlays Toggle */}
            <div className="flex items-center gap-4 text-xs text-slate-300">
              <label className="inline-flex items-center gap-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showBoxes}
                  onChange={(e) => setShowBoxes(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-emerald-500 focus:ring-0"
                />
                <span>Bounding Boxes</span>
              </label>

              <label className="inline-flex items-center gap-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showGaps}
                  onChange={(e) => setShowGaps(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-red-500 focus:ring-0"
                />
                <span>Out-of-Stock Gaps</span>
              </label>
            </div>
          </div>

          {/* Interactive Image & Overlay Container */}
          <div className="mt-4 relative bg-slate-950 rounded-lg overflow-hidden border border-slate-700/60 flex items-center justify-center min-h-[420px]">
            {loading && (
              <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center z-20">
                <div className="flex flex-col items-center gap-2 text-sm text-slate-200">
                  <span className="animate-spin text-2xl">🔄</span>
                  <span>Running YOLO Object Detection...</span>
                </div>
              </div>
            )}

            {error && (
              <div className="absolute top-4 left-4 right-4 bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg text-xs z-30 flex items-center justify-between">
                <span>{error}</span>
                <button
                  onClick={runAnalysis}
                  className="px-2.5 py-1 bg-red-500/20 hover:bg-red-500/30 rounded"
                >
                  Retry
                </button>
              </div>
            )}

            {currentImageUrl ? (
              <div className="relative inline-block max-w-full max-h-[560px]">
                <img
                  src={currentImageUrl}
                  alt="Shelf View"
                  className="block max-h-[560px] w-auto object-contain rounded"
                />

                {/* SVG Overlay for Bounding Boxes and Gaps */}
                <svg
                  className="absolute inset-0 w-full h-full pointer-events-none"
                  viewBox="0 0 1 1"
                  preserveAspectRatio="none"
                >
                  {/* Render Product Bounding Boxes */}
                  {showBoxes &&
                    analysis?.detections.map((box, idx) => {
                      const isHovered = hoveredBox === box;
                      return (
                        <g key={`box-${idx}`} className="pointer-events-auto cursor-pointer">
                          <rect
                            x={box.x_min}
                            y={box.y_min}
                            width={box.x_max - box.x_min}
                            height={box.y_max - box.y_min}
                            fill={isHovered ? 'rgba(16, 185, 129, 0.25)' : 'rgba(16, 185, 129, 0.08)'}
                            stroke={isHovered ? '#34d399' : '#10b981'}
                            strokeWidth={isHovered ? '0.003' : '0.0018'}
                            onMouseEnter={() => setHoveredBox(box)}
                            onMouseLeave={() => setHoveredBox(null)}
                          />
                        </g>
                      );
                    })}

                  {/* Render Out-of-Stock Gap Overlays */}
                  {showGaps &&
                    analysis?.detected_gaps.map((gap, idx) => {
                      const isHovered = hoveredGap === gap;
                      return (
                        <g key={`gap-${idx}`} className="pointer-events-auto cursor-pointer">
                          <rect
                            x={gap.gap_x_start}
                            y={0.15 * gap.shelf_row}
                            width={gap.gap_width}
                            height={0.12}
                            fill="rgba(239, 68, 68, 0.18)"
                            stroke="#ef4444"
                            strokeWidth={isHovered ? '0.003' : '0.002'}
                            strokeDasharray="0.004, 0.004"
                            onMouseEnter={() => setHoveredGap(gap)}
                            onMouseLeave={() => setHoveredGap(null)}
                          />
                        </g>
                      );
                    })}
                </svg>

                {/* Tooltip Overlay */}
                {hoveredBox && (
                  <div
                    className="absolute bg-slate-900/90 text-slate-100 text-[10px] px-2 py-1 rounded shadow-lg border border-slate-700 pointer-events-none z-30"
                    style={{
                      left: `${hoveredBox.x_min * 100}%`,
                      top: `${Math.max(0, (hoveredBox.y_min - 0.04) * 100)}%`,
                    }}
                  >
                    {hoveredBox.class_name} • {(hoveredBox.confidence * 100).toFixed(1)}% conf
                  </div>
                )}

                {hoveredGap && (
                  <div
                    className="absolute bg-red-950/90 text-red-200 text-[10px] px-2 py-1 rounded shadow-lg border border-red-700 pointer-events-none z-30"
                    style={{
                      left: `${hoveredGap.gap_x_start * 100}%`,
                      top: `${0.15 * hoveredGap.shelf_row * 100}%`,
                    }}
                  >
                    Tier {hoveredGap.shelf_row} Gap • ~{hoveredGap.estimated_missing_units} units missing
                  </div>
                )}
              </div>
            ) : (
              <div className="py-20 text-slate-500 text-sm">No image loaded.</div>
            )}
          </div>

          {/* Footer Metadata */}
          {analysis && (
            <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
              <span>
                Input Resolution: {analysis.image_width} × {analysis.image_height} px
              </span>
              <span className="text-[11px] text-slate-500 italic">
                {analysis.disclaimer}
              </span>
            </div>
          )}
        </div>

        {/* Controls & Out-of-Stock Alerts Panel (Right/Bottom) */}
        <div className="lg:col-span-12 xl:col-span-4 space-y-4">
          {/* Preset Sample Selector Card */}
          <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-slate-100 mb-3">
              1. Choose Shelf Scene
            </h2>

            <div className="space-y-2">
              {samples.map((s) => {
                const isSelected = selectedSampleId === s.sample_id && !uploadedFile;
                return (
                  <div
                    key={s.sample_id}
                    onClick={() => handleSelectSample(s.sample_id)}
                    className={`p-3 rounded-lg border cursor-pointer transition text-xs ${
                      isSelected
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-slate-100'
                        : 'bg-slate-900/50 border-slate-700/50 text-slate-300 hover:bg-slate-700/40'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold">
                      <span>{s.title}</span>
                      <span className="font-mono text-[10px] text-slate-400">{s.filename}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">{s.description}</p>
                  </div>
                );
              })}
            </div>

            {/* Custom Upload Input */}
            <div className="mt-4 pt-4 border-t border-slate-700/60">
              <input
                type="file"
                ref={fileInputRef}
                accept="image/jpeg,image/png"
                onChange={handleFileChange}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full py-2 px-3 text-xs font-medium rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition flex items-center justify-center gap-2"
              >
                <span>📁</span>
                {uploadedFile ? `Loaded: ${uploadedFile.name}` : 'Upload Custom Shelf Photo'}
              </button>
            </div>
          </div>

          {/* Model Parameters Card */}
          <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-slate-100 mb-3">
              2. Vision Model Parameters
            </h2>

            <div className="space-y-4 text-xs">
              <div>
                <div className="flex items-center justify-between text-slate-300 mb-1.5">
                  <span>Confidence Threshold:</span>
                  <span className="font-mono text-emerald-400 font-semibold">
                    {(confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.80"
                  step="0.05"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                  <span>5% (High Recall)</span>
                  <span>80% (High Precision)</span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-700/40 text-[11px] text-slate-400 space-y-1">
                <div>• Architecture: Ultralytics YOLOv8 Nano</div>
                <div>• Target Resolution: 640×640 inference scaled</div>
                <div>• Dataset Standard: SKU-110K retail shelf format</div>
              </div>
            </div>
          </div>

          {/* Out-of-Stock Gaps Alert List */}
          <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-1.5">
                <span>⚠️</span>
                Shelf Gaps & Restock Triggers
              </h2>
              <span className="text-xs text-slate-400 font-mono">
                {analysis ? `${analysis.detected_gaps.length} gaps` : '—'}
              </span>
            </div>

            {analysis && analysis.detected_gaps.length > 0 ? (
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {analysis.detected_gaps.map((gap, idx) => (
                  <div
                    key={idx}
                    onMouseEnter={() => setHoveredGap(gap)}
                    onMouseLeave={() => setHoveredGap(null)}
                    className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-700/50 flex items-center justify-between text-xs hover:border-red-500/50 transition"
                  >
                    <div>
                      <div className="font-semibold text-slate-200">
                        Shelf Row {gap.shelf_row} Gap
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Span: {(gap.gap_width * 100).toFixed(0)}% width • ~{gap.estimated_missing_units} units missing
                      </div>
                    </div>

                    <span
                      className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        gap.severity === 'HIGH'
                          ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                          : gap.severity === 'MEDIUM'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                          : 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                      }`}
                    >
                      {gap.severity}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center text-slate-500 text-xs">
                {analysis ? '✓ No critical stockout gaps detected on this shelf.' : 'Run analysis to detect shelf gaps.'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
