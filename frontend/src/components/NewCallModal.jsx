import { useRef } from 'react';
import { X, Music, FileText, Info } from 'lucide-react';
import { addUploadedCall } from '../data/callStore.js';

export default function NewCallModal({ isOpen, onClose, onCallCreated }) {
  const audioInputRef      = useRef(null);
  const transcriptInputRef = useRef(null);

  if (!isOpen) return null;

  function handleAudioSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const audioSrc = URL.createObjectURL(file);
    const callId = addUploadedCall(file, 'audio', null, audioSrc);
    e.target.value = '';
    onClose();
    onCallCreated(callId);
  }

  function handleTranscriptSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const rawText = evt.target?.result || '';
      const callId  = addUploadedCall(file, 'transcript', rawText);
      e.target.value = '';
      onClose();
      onCallCreated(callId);
    };
    reader.onerror = () => {
      const callId = addUploadedCall(file, 'transcript', null);
      e.target.value = '';
      onClose();
      onCallCreated(callId);
    };
    reader.readAsText(file);
  }

  return (
    /* Overlay */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Modal card */}
      <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl p-6">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          aria-label="Close"
        >
          <X size={18} />
        </button>

        {/* Header */}
        <div className="mb-5">
          <h2 className="text-[20px] font-bold text-slate-800">New Call</h2>
          <p className="text-[14px] text-slate-500 mt-1">
            Choose how you want to create a new call for analysis
          </p>
        </div>

        {/* Option cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
          {/* Audio option */}
          <button
            type="button"
            onClick={() => audioInputRef.current?.click()}
            className="flex flex-col items-start gap-3 border-2 border-slate-200 rounded-xl p-4 text-left hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
              <Music size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-[14px] font-semibold text-slate-800">Upload Audio File</p>
              <p className="text-[12px] text-slate-500 mt-0.5">Upload a call audio file (MP3, WAV, M4A)</p>
            </div>
          </button>

          {/* Transcript option */}
          <button
            type="button"
            onClick={() => transcriptInputRef.current?.click()}
            className="flex flex-col items-start gap-3 border-2 border-slate-200 rounded-xl p-4 text-left hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
              <FileText size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-[14px] font-semibold text-slate-800">Upload Transcript File</p>
              <p className="text-[12px] text-slate-500 mt-0.5">Upload a transcript file (TXT)</p>
            </div>
          </button>
        </div>

        {/* Note box */}
        <div className="flex items-start gap-2.5 bg-blue-50 border border-blue-100 rounded-lg px-4 py-3 mb-5">
          <Info size={15} className="text-blue-500 flex-shrink-0 mt-0.5" />
          <p className="text-[13px] text-blue-700 leading-relaxed">
            The file will be processed and analyzed to generate insights, summaries, and compliance results.
          </p>
        </div>

        {/* Footer */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-slate-200 rounded-lg text-[13px] text-slate-600 font-medium hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
        </div>

        {/* Hidden file inputs */}
        <input
          ref={audioInputRef}
          type="file"
          accept=".mp3,.wav,.m4a,audio/*"
          className="hidden"
          onChange={handleAudioSelect}
        />
        <input
          ref={transcriptInputRef}
          type="file"
          accept=".txt,text/plain"
          className="hidden"
          onChange={handleTranscriptSelect}
        />
      </div>
    </div>
  );
}
