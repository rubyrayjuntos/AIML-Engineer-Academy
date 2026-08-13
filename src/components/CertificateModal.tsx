import React, { useEffect, useMemo, useState } from 'react';
import { Award, CheckCircle2, X, Download, ShieldCheck, Lock } from 'lucide-react';
import { UserProgress } from '../types';
import { evaluateCertificateEligibility } from '../certificateEligibility';

interface CertificateModalProps {
  isOpen: boolean;
  onClose: () => void;
  progress: UserProgress;
  onGrantCertificate: () => void;
}

export { evaluateCertificateEligibility } from '../certificateEligibility';

export const CertificateModal: React.FC<CertificateModalProps> = ({
  isOpen,
  onClose,
  progress,
  onGrantCertificate
}) => {
  const [studentName, setStudentName] = useState('Senior AI Systems Engineer');
  const eligibility = useMemo(() => evaluateCertificateEligibility(progress), [progress]);

  useEffect(() => {
    if (isOpen && eligibility.eligible && !progress.certificateGranted) {
      onGrantCertificate();
    }
  }, [isOpen, eligibility.eligible, progress.certificateGranted, onGrantCertificate]);

  if (!isOpen) return null;

  if (!eligibility.eligible) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl w-full max-w-xl p-6 md:p-8 border border-slate-200 shadow-2xl relative">
          <button
            onClick={onClose}
            className="absolute top-6 right-6 p-2 text-slate-400 hover:text-slate-800 bg-slate-100 rounded-xl transition-all"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-2xl bg-slate-900 text-amber-400 flex items-center justify-center">
              <Lock className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-black text-slate-900">Certificate Locked</h2>
              <p className="text-xs text-slate-500">Finish the requirements below to unlock the Neural Academy certificate.</p>
            </div>
          </div>

          <ul className="space-y-3">
            {eligibility.checks.map(check => (
              <li
                key={check.id}
                className={`rounded-2xl border px-4 py-3 ${
                  check.done ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-slate-50'
                }`}
              >
                <div className="flex items-start gap-2">
                  <CheckCircle2 className={`w-4 h-4 mt-0.5 ${check.done ? 'text-emerald-600' : 'text-slate-400'}`} />
                  <div>
                    <p className="text-sm font-bold text-slate-900">{check.label}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{check.detail}</p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-4xl p-6 md:p-10 border border-slate-200 shadow-2xl relative overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 text-slate-400 hover:text-slate-800 bg-slate-100 rounded-xl transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="border-8 border-slate-900 rounded-2xl p-8 md:p-12 text-center space-y-6 relative bg-gradient-to-b from-slate-50 to-white">
          <div className="flex justify-center mb-2">
            <div className="w-16 h-16 rounded-3xl bg-amber-500 text-slate-950 flex items-center justify-center shadow-lg shadow-amber-200">
              <Award className="w-10 h-10" />
            </div>
          </div>

          <span className="text-xs font-mono font-bold uppercase tracking-widest text-amber-600 block">
            Neural Academy Certificate of Completion
          </span>

          <h1 className="text-3xl md:text-5xl font-black text-slate-900 tracking-tight font-serif">
            Master AI Engineer Specialist
          </h1>

          <p className="text-sm text-slate-500 max-w-lg mx-auto leading-relaxed">
            This learning credential recognizes completion of all five technical modules, confirmed lab evidence,
            and a passing knowledge assessment covering attention kernels, agent orchestration, secure serving, and production operations.
            It is issued by this training app and is not an official certification from Google, xAI, or any cloud vendor.
          </p>

          <div className="max-w-md mx-auto py-2">
            <input
              type="text"
              value={studentName}
              onChange={(e) => setStudentName(e.target.value)}
              className="w-full text-center text-xl font-bold text-slate-900 border-b-2 border-slate-900 py-1 bg-transparent focus:outline-none"
              placeholder="Enter Your Full Name"
            />
            <span className="text-[10px] text-slate-400 font-mono mt-1 block">Graduate Name</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left pt-6 border-t border-slate-200">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Level Designation</span>
              <span className="text-xs font-bold text-slate-900 font-mono">{progress.userLevel}</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Credential ID</span>
              <span className="text-xs font-bold text-slate-900 font-mono">NA-LEARN-{progress.completedModules.length}M</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Issue Date</span>
              <span className="text-xs font-bold text-slate-900 font-mono">{new Date().toISOString().split('T')[0]}</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Status</span>
              <span className="text-xs font-bold text-emerald-600 font-mono flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Requirements Met
              </span>
            </div>
          </div>
        </div>

        <div className="flex justify-between items-center mt-6">
          <span className="text-xs text-slate-500">
            Portfolio keepsake for this learning path — not a third-party accredited certificate.
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
