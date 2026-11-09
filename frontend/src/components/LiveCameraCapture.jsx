/**
 * components/LiveCameraCapture.jsx - Roadside Live Camera Capture Component
 * =========================================================================
 * Smart ANPR Vehicle Verification System
 * Design: White and Blue Professional Enterprise SaaS UI
 *
 * Implements:
 * - HTML5 MediaDevices (navigator.mediaDevices.getUserMedia) camera integration
 * - Automatic rear-camera preference (facingMode: 'environment') for roadside patrol
 * - Front/rear camera device switching when multiple cameras exist
 * - Targeting reticle / license plate alignment guides over the live stream
 * - High-resolution frame capture using HTML Canvas -> JPEG File
 * - Retake photo and Confirm & Process workflows
 * - Full hardware resource cleanup on stop, retake, or unmount
 * - Comprehensive browser permission and device error handling
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Camera,
  CameraOff,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  FlipHorizontal,
  Sparkles,
  Shield,
  Video,
} from 'lucide-react';

export default function LiveCameraCapture({ onPhotoCaptured, isProcessing, showToast }) {
  const [cameraActive, setCameraActive] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);
  const [capturedPreview, setCapturedPreview] = useState(null);
  const [capturedFile, setCapturedFile] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const [facingMode, setFacingMode] = useState('environment'); // 'environment' | 'user'
  const [availableDevices, setAvailableDevices] = useState([]);
  const [currentDeviceId, setCurrentDeviceId] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  // Stop camera tracks and release hardware
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // Ignore track stop errors
        }
      });
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCameraActive(false);
    setIsInitializing(false);
  }, []);

  // Enumerate available video inputs
  const checkDevices = async () => {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = devices.filter((d) => d.kind === 'videoinput');
      setAvailableDevices(videoInputs);
    } catch {
      // Ignore device enumeration failure
    }
  };

  // Start camera stream
  const startCamera = async (targetFacing = facingMode, targetDeviceId = currentDeviceId) => {
    setCameraError(null);
    setIsInitializing(true);
    setCapturedPreview(null);
    setCapturedFile(null);

    // Ensure previous stream is cleanly stopped
    stopCamera();

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setCameraError('Camera access (MediaDevices API) is not supported by your browser or environment.');
      setIsInitializing(false);
      return;
    }

    // Build constraints: prefer rear camera ('environment') on mobile devices
    const constraints = {
      audio: false,
      video: targetDeviceId
        ? { deviceId: { exact: targetDeviceId } }
        : {
            facingMode: { ideal: targetFacing },
            width: { ideal: 1920 },
            height: { ideal: 1080 },
          },
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = async () => {
          try {
            await videoRef.current.play();
            setCameraActive(true);
            setIsInitializing(false);
            checkDevices();
          } catch (playErr) {
            setCameraError(`Camera playback error: ${playErr.message}`);
            setIsInitializing(false);
          }
        };
      }
    } catch (err) {
      setIsInitializing(false);
      setCameraActive(false);

      let msg = 'Failed to access camera.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = 'Camera permission was denied. Please allow camera access in your browser site settings.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = 'No camera device was detected on your computer or phone.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        msg = 'Camera is already in use by another application or browser tab.';
      } else if (err.name === 'OverconstrainedError') {
        try {
          const fallbackStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
          streamRef.current = fallbackStream;
          if (videoRef.current) {
            videoRef.current.srcObject = fallbackStream;
            await videoRef.current.play();
            setCameraActive(true);
            return;
          }
        } catch {
          msg = 'Camera constraints could not be satisfied by your video hardware.';
        }
      } else {
        msg = err.message || msg;
      }

      setCameraError(msg);
      showToast?.({
        type: 'error',
        title: 'Camera Error',
        message: msg,
      });
    }
  };

  // Flip front/rear camera
  const handleToggleCamera = () => {
    const nextMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextMode);

    if (availableDevices.length > 1) {
      const currIdx = availableDevices.findIndex((d) => d.deviceId === currentDeviceId);
      const nextIdx = (currIdx + 1) % availableDevices.length;
      const nextDevice = availableDevices[nextIdx];
      setCurrentDeviceId(nextDevice.deviceId);
      startCamera(nextMode, nextDevice.deviceId);
    } else {
      startCamera(nextMode, null);
    }
  };

  // Snap photo from video stream using offscreen canvas
  const handleCapturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, width, height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          showToast?.({
            type: 'error',
            title: 'Capture Failed',
            message: 'Could not extract photo frame from video stream.',
          });
          return;
        }

        const now = new Date();
        const timestamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;
        const filename = `roadside_camera_${timestamp}.jpg`;
        const file = new File([blob], filename, { type: 'image/jpeg' });
        const previewUrl = URL.createObjectURL(blob);

        setCapturedFile(file);
        setCapturedPreview(previewUrl);

        // Stop video stream after capture to conserve power & release hardware
        stopCamera();

        showToast?.({
          type: 'info',
          title: 'Photo Captured',
          message: `Frame captured at ${width}x${height} resolution. Review and confirm to process.`,
        });
      },
      'image/jpeg',
      0.95
    );
  };

  // Retake photo: clear capture and restart live camera
  const handleRetake = () => {
    if (capturedPreview) {
      URL.revokeObjectURL(capturedPreview);
    }
    setCapturedPreview(null);
    setCapturedFile(null);
    startCamera(facingMode, currentDeviceId);
  };

  // Confirm photo and forward to parent processing pipeline
  const handleConfirmAndProcess = () => {
    if (!capturedFile) return;
    if (onPhotoCaptured) {
      onPhotoCaptured(capturedFile, capturedPreview);
    }
  };

  // Cleanup camera stream when component unmounts
  useEffect(() => {
    return () => {
      stopCamera();
      if (capturedPreview) {
        URL.revokeObjectURL(capturedPreview);
      }
    };
  }, [stopCamera, capturedPreview]);

  return (
    <div className="space-y-4">
      {/* Hidden canvas for taking snapshot */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Main Viewport Container */}
      <div className="relative rounded-2xl border border-[#DCE3EC] bg-slate-900 overflow-hidden shadow-sm min-h-[380px] flex items-center justify-center">
        {capturedPreview ? (
          /* Captured Photo Review Mode */
          <div className="relative w-full h-full flex flex-col items-center justify-center p-2 bg-slate-950">
            <img
              src={capturedPreview}
              alt="Roadside Capture Preview"
              className="max-h-[440px] w-full object-contain rounded-xl shadow-lg border border-slate-700"
            />
            {/* Overlay badge */}
            <div className="absolute top-4 left-4 bg-white/95 text-[#172B4D] border border-[#DCE3EC] px-3.5 py-1.5 rounded-full text-xs font-semibold backdrop-blur-md flex items-center gap-1.5 shadow-md">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span>Photo Captured &bull; Ready for AI Inference</span>
            </div>
          </div>
        ) : (
          /* Live Camera Stream Mode */
          <div className="relative w-full h-full min-h-[380px] flex items-center justify-center bg-slate-950">
            {/* HTML5 Video Preview */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full max-h-[440px] object-cover transition-opacity duration-300 ${
                cameraActive ? 'opacity-100' : 'opacity-0'
              }`}
            />

            {/* Inactive State Prompt */}
            {!cameraActive && !isInitializing && (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center space-y-4 bg-white">
                <div className="h-16 w-16 rounded-2xl bg-[#EFF5FF] border border-[#DCE3EC] flex items-center justify-center text-[#1769D2] shadow-sm">
                  <Camera className="h-8 w-8" />
                </div>
                <div className="max-w-sm space-y-1">
                  <h3 className="text-base font-bold text-[#172B4D]">
                    Roadside Live Camera Patrol
                  </h3>
                  <p className="text-xs text-[#64748B] leading-relaxed">
                    Capture vehicle license plates directly using your device camera. Supports front/rear cameras on mobile phones, tablets, and field workstations.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => startCamera()}
                  className="px-6 py-3 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs flex items-center gap-2 transition-all shadow-sm"
                >
                  <Camera className="h-4 w-4" />
                  <span>Start Live Camera</span>
                </button>
              </div>
            )}

            {/* Initializing Spinner */}
            {isInitializing && (
              <div className="absolute inset-0 bg-white/90 flex flex-col items-center justify-center p-6 text-center space-y-3 backdrop-blur-sm">
                <RefreshCw className="h-8 w-8 animate-spin text-[#1769D2]" />
                <p className="text-sm font-semibold text-[#172B4D]">
                  Requesting camera permissions & initializing stream...
                </p>
                <p className="text-xs text-[#64748B]">
                  Please click &quot;Allow&quot; in the browser prompt if requested.
                </p>
              </div>
            )}

            {/* Error Overlay */}
            {cameraError && !isInitializing && (
              <div className="absolute inset-0 bg-white/95 flex flex-col items-center justify-center p-6 text-center space-y-3">
                <div className="h-12 w-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center border border-rose-200">
                  <AlertTriangle className="h-6 w-6" />
                </div>
                <h4 className="text-sm font-bold text-[#172B4D]">Camera Access Blocked</h4>
                <p className="text-xs text-rose-600 max-w-sm leading-relaxed">{cameraError}</p>
                <button
                  type="button"
                  onClick={() => startCamera()}
                  className="px-4 py-2 bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] rounded-lg text-xs font-semibold border border-[#DCE3EC] transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}

            {/* Targeting Reticle & Alignment Guides (When camera is live) */}
            {cameraActive && (
              <div className="absolute inset-0 pointer-events-none flex flex-col items-center justify-between p-6">
                {/* Top Status Badge */}
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center gap-2 bg-white/90 border border-[#DCE3EC] px-3.5 py-1.5 rounded-full text-[11px] font-semibold text-[#172B4D] backdrop-blur-md shadow-sm">
                    <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span>
                      Live Video ({facingMode === 'environment' ? 'Rear Camera' : 'Front Camera'})
                    </span>
                  </div>

                  <span className="text-[10px] bg-[#1769D2] text-white font-mono px-2.5 py-1 rounded-md uppercase font-bold shadow-sm">
                    ANPR AI Ready
                  </span>
                </div>

                {/* Center License Plate Targeting Reticle */}
                <div className="relative w-72 sm:w-96 h-28 border-2 border-dashed border-white/80 rounded-xl bg-blue-500/10 flex items-center justify-center shadow-lg">
                  {/* Four Corner Alignment Brackets */}
                  <div className="absolute -top-2 -left-2 w-5 h-5 border-t-4 border-l-4 border-amber-400 rounded-tl"></div>
                  <div className="absolute -top-2 -right-2 w-5 h-5 border-t-4 border-r-4 border-amber-400 rounded-tr"></div>
                  <div className="absolute -bottom-2 -left-2 w-5 h-5 border-b-4 border-l-4 border-amber-400 rounded-bl"></div>
                  <div className="absolute -bottom-2 -right-2 w-5 h-5 border-b-4 border-r-4 border-amber-400 rounded-br"></div>

                  <div className="text-center px-4 py-1.5 rounded-lg bg-white/95 border border-[#DCE3EC] text-[#172B4D] text-[11px] font-bold shadow">
                    Align Vehicle License Plate Inside This Frame
                  </div>
                </div>

                {/* Bottom Guide Notice */}
                <div className="text-[11px] text-[#172B4D] font-medium bg-white/90 px-4 py-1 rounded-full border border-[#DCE3EC] shadow-sm">
                  Hold steady and tap the shutter button below
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Control Actions Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-white border border-[#DCE3EC] shadow-sm">
        {capturedPreview ? (
          /* Captured Photo Actions: Retake vs Confirm */
          <div className="flex items-center justify-between w-full gap-3">
            <button
              type="button"
              onClick={handleRetake}
              disabled={isProcessing}
              className="px-4 py-2.5 rounded-xl bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] font-semibold text-xs border border-[#DCE3EC] flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Retake Photo</span>
            </button>

            <button
              type="button"
              onClick={handleConfirmAndProcess}
              disabled={isProcessing}
              className="px-6 py-2.5 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs flex items-center gap-2 transition-all shadow-sm disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Processing with AI Pipeline...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 text-amber-300" />
                  <span>Confirm & Process with AI</span>
                </>
              )}
            </button>
          </div>
        ) : cameraActive ? (
          /* Live Stream Active Actions: Stop, Flip, Capture */
          <div className="flex items-center justify-between w-full">
            <button
              type="button"
              onClick={stopCamera}
              className="px-3.5 py-2 rounded-xl bg-white hover:bg-rose-50 hover:text-rose-600 text-[#64748B] font-semibold text-xs border border-[#DCE3EC] flex items-center gap-1.5 transition-colors"
              title="Stop live camera stream"
            >
              <CameraOff className="h-4 w-4" />
              <span className="hidden sm:inline">Close Camera</span>
            </button>

            {/* Shutter Button */}
            <button
              type="button"
              onClick={handleCapturePhoto}
              className="px-8 py-3 rounded-full bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs flex items-center gap-2.5 transition-all shadow-md border-2 border-white transform active:scale-95"
            >
              <span className="h-2.5 w-2.5 rounded-full bg-white animate-ping"></span>
              <Camera className="h-4 w-4" />
              <span>Capture Photo</span>
            </button>

            {/* Camera Switch / Flip Button */}
            <button
              type="button"
              onClick={handleToggleCamera}
              className="px-3.5 py-2 rounded-xl bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] font-semibold text-xs border border-[#DCE3EC] flex items-center gap-1.5 transition-colors"
              title="Switch front / rear camera"
            >
              <FlipHorizontal className="h-4 w-4" />
              <span className="hidden sm:inline">Switch Lens</span>
            </button>
          </div>
        ) : (
          /* Idle Action: Start Camera */
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2 text-xs text-[#64748B]">
              <Shield className="h-4 w-4 text-[#1769D2]" />
              <span>Roadside field officer camera mode ready</span>
            </div>

            <button
              type="button"
              onClick={() => startCamera()}
              className="px-5 py-2.5 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs flex items-center gap-2 transition-all shadow-sm"
            >
              <Camera className="h-4 w-4" />
              <span>Start Camera</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
