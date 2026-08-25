import React from 'react';

interface ModulePlaceholderProps {
  title: string;
  stage: string;
  category: string;
  description: string;
  objectives: string[];
  inputs: string[];
  outputs: string[];
  badgeColor?: string;
}

export const ModulePlaceholder: React.FC<ModulePlaceholderProps> = ({
  title,
  stage,
  category,
  description,
  objectives,
  inputs,
  outputs,
  badgeColor = 'bg-blue-100 text-blue-800 border-blue-200',
}) => {
  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeColor}`}
              >
                {stage}
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-1 font-medium">Category: {category}</p>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span>
            Planned Module — Awaiting {stage}
          </div>
        </div>
        <p className="mt-4 text-slate-700 leading-relaxed text-sm">{description}</p>
      </div>

      {/* Specification Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Objectives */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-base font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <span className="w-6 h-6 rounded-md bg-indigo-50 text-indigo-600 inline-flex items-center justify-center text-xs font-bold">
              1
            </span>
            Core Objectives
          </h2>
          <ul className="space-y-2 text-sm text-slate-600">
            {objectives.map((obj, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-indigo-500 font-bold mt-0.5">•</span>
                <span>{obj}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Inputs */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-base font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <span className="w-6 h-6 rounded-md bg-emerald-50 text-emerald-600 inline-flex items-center justify-center text-xs font-bold">
              2
            </span>
            Expected Inputs & Data
          </h2>
          <ul className="space-y-2 text-sm text-slate-600">
            {inputs.map((inp, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-500 font-bold mt-0.5">•</span>
                <span>{inp}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Outputs */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-base font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <span className="w-6 h-6 rounded-md bg-amber-50 text-amber-600 inline-flex items-center justify-center text-xs font-bold">
              3
            </span>
            Intelligence Outputs
          </h2>
          <ul className="space-y-2 text-sm text-slate-600">
            {outputs.map((out, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-amber-500 font-bold mt-0.5">•</span>
                <span>{out}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Notice Card */}
      <div className="bg-slate-50 border border-dashed border-slate-300 rounded-xl p-6 text-center text-slate-600 text-sm">
        <p className="font-medium text-slate-700">Incremental Development Policy</p>
        <p className="mt-1 text-xs text-slate-500">
          Per <code className="px-1.5 py-0.5 bg-slate-200 rounded text-slate-800">AGENTS.md</code>, this AI module will be developed in its designated milestone after foundation and dataset validation are complete.
        </p>
      </div>
    </div>
  );
};
