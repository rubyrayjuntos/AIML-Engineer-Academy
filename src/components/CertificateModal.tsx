import React, { useState } from 'react';
import { Award, CheckCircle2, X, Download, ShieldCheck } from 'lucide-react';

interface CertificateModalProps {
  isOpen: boolean;
  onClose: () => void;
  userLevel: string;
}

export const CertificateModal: React.FC<CertificateModalProps> = ({ isOpen, onClose, userLevel }) => {
  const [studentName, setStudentName] = useState('Senior AI Systems Engineer');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-4xl p-6 md:p-10 border border-slate-200 shadow-2xl relative overflow-hidden">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 text-slate-400 hover:text-slate-800 bg-slate-100 rounded-xl transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Certificate Frame */}
        <div className="border-8 border-slate-900 rounded-2xl p-8 md:p-12 text-center space-y-6 relative bg-gradient-to-b from-slate-50 to-white">
          <div className="flex justify-center mb-2">
            <div className="w-16 h-16 rounded-3xl bg-amber-500 text-slate-950 flex items-center justify-center shadow-lg shadow-amber-200">
              <Award className="w-10 h-10" />
            </div>
          </div>

          <span className="text-xs font-mono font-bold uppercase tracking-widest text-amber-600 block">
            Google AI Studio Certification of Mastery
          </span>

          <h1 className="text-3xl md:text-5xl font-black text-slate-900 tracking-tight font-serif">
            Master AI Engineer Specialist
          </h1>

          <p className="text-sm text-slate-500 max-w-lg mx-auto leading-relaxed">
            This official credential certifies that the candidate has successfully completed all 5 technical modules covering GPU attention kernels, LLM memory architectures, agentic orchestration, systems optimization, and cloud deployment.
          </p>

          <div className="max-w-md mx-auto py-2">
            <input
              type="text"
              value={studentName}
              onChange={(e) => setStudentName(e.target.value)}
              className="w-full text-center text-xl font-bold text-slate-900 border-b-2 border-slate-900 py-1 bg-transparent focus:outline-none"
              placeholder="Enter Your Full Name"
            />
            <span className="text-[10px] text-slate-400 font-mono mt-1 block">Certified Graduate Name</span>
          </div>

          {/* Verification Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left pt-6 border-t border-slate-200">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Level Designation</span>
              <span className="text-xs font-bold text-slate-900 font-mono">{userLevel}</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Credential ID</span>
              <span className="text-xs font-bold text-slate-900 font-mono">AIE-2026-9941X</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Issue Date</span>
              <span className="text-xs font-bold text-slate-900 font-mono">{new Date().toISOString().split('T')[0]}</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Verification</span>
              <span className="text-xs font-bold text-emerald-600 font-mono flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Verified
              </span>
            </div>
          </div>
        </div>

        {/* Modal Action Footer */}
        <div className="flex justify-between items-center mt-6">
          <span className="text-xs text-slate-500">
            You can print or download this certificate for your professional portfolio.
          </span>

          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-md transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download / Print PDF</span>
          </button>
        </div>
      </div>
    </div>
  );
};
