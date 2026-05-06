import { useRef, useState, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Download } from 'lucide-react';

function formatTime(seconds) {
  if (!isFinite(seconds) || isNaN(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function AudioPlayer({ src }) {
  const audioRef             = useRef(null);
  const [playing, setPlaying]   = useState(false);
  const [muted, setMuted]       = useState(false);
  const [current, setCurrent]   = useState(0);
  const [duration, setDuration] = useState(0);
  const [loadError, setLoadError] = useState(false);

  const hasAudio = Boolean(src) && !loadError;

  useEffect(() => {
    setPlaying(false);
    setCurrent(0);
    setDuration(0);
    setLoadError(false);
  }, [src]);

  const togglePlay = () => {
    if (!audioRef.current || !hasAudio) return;
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(() => setLoadError(true));
    }
    setPlaying((p) => !p);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) setCurrent(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) setDuration(audioRef.current.duration);
  };

  const handleEnded = () => setPlaying(false);

  const handleSeek = (e) => {
    if (!audioRef.current || !hasAudio) return;
    const t = Number(e.target.value);
    audioRef.current.currentTime = t;
    setCurrent(t);
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    audioRef.current.muted = !muted;
    setMuted((m) => !m);
  };

  const progress = duration > 0 ? (current / duration) * 100 : 0;

  // Waveform bars — decorative
  const bars = Array.from({ length: 40 }, (_, i) => {
    const heights = [3,5,8,12,9,6,10,14,11,7,4,9,13,10,8,5,12,15,11,7,4,8,13,10,6,9,14,11,7,5,8,12,10,7,4,9,13,10,6,5];
    return heights[i] || 6;
  });

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-card p-4">
      <p className="text-[13px] font-semibold text-slate-500 uppercase tracking-wide mb-3">Call Audio</p>

      {/* Hidden real audio element */}
      {src && (
        <audio
          ref={audioRef}
          src={src}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={handleEnded}
          onError={() => setLoadError(true)}
          preload="metadata"
        />
      )}

      {/* Player row */}
      <div className="flex items-center gap-3">
        {/* Play / Pause button */}
        <button
          onClick={togglePlay}
          disabled={!hasAudio}
          className={`flex items-center justify-center w-10 h-10 rounded-full flex-shrink-0 transition-colors ${
            hasAudio
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed'
          }`}
        >
          {playing ? <Pause size={16} fill="currentColor" /> : <Play size={16} fill="currentColor" className="ml-0.5" />}
        </button>

        {/* Time + waveform + scrubber */}
        <div className="flex-1 min-w-0">
          {/* Waveform + scrubber */}
          <div className="relative h-8 flex items-center gap-[2px] mb-1">
            {bars.map((h, i) => {
              const pct = duration > 0 ? (i / bars.length) * 100 : 0;
              const filled = pct <= progress;
              return (
                <div
                  key={i}
                  style={{ height: `${h * 2}px` }}
                  className={`w-[3px] rounded-full flex-shrink-0 transition-colors ${
                    hasAudio && filled ? 'bg-blue-500' : 'bg-slate-200'
                  }`}
                />
              );
            })}
            {/* Invisible range input on top for seeking */}
            <input
              type="range"
              min={0}
              max={duration || 100}
              step={0.1}
              value={current}
              onChange={handleSeek}
              disabled={!hasAudio}
              className="absolute inset-0 w-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
            />
          </div>

          {/* Time display */}
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>{formatTime(current)}</span>
            <span>{hasAudio && duration > 0 ? formatTime(duration) : '--:--'}</span>
          </div>
        </div>

        {/* Volume */}
        <button
          onClick={toggleMute}
          disabled={!hasAudio}
          className={`transition-colors flex-shrink-0 ${hasAudio ? 'text-slate-400 hover:text-slate-600' : 'text-slate-300 cursor-not-allowed'}`}
        >
          {muted ? <VolumeX size={18} /> : <Volume2 size={18} />}
        </button>

        {/* Download */}
        {src && !loadError ? (
          <a href={src} download className="text-slate-400 hover:text-slate-600 flex-shrink-0">
            <Download size={18} />
          </a>
        ) : (
          <button disabled className="text-slate-300 cursor-not-allowed flex-shrink-0">
            <Download size={18} />
          </button>
        )}
      </div>

      {/* No audio message */}
      {!hasAudio && (
        <p className="mt-2 text-[12px] text-slate-400 text-center">
          No audio file available for this call.
        </p>
      )}
    </div>
  );
}
