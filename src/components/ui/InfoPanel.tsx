import { useAnatomyStore } from '@/store';
import { getStructureById, getContentForStructure } from '@/data';

/**
 * Information panel that displays details about the selected structure.
 * Shows different content based on the current view mode (fitness vs clinical).
 */
export function InfoPanel() {
  const {
    selectedStructureId,
    viewMode,
    infoPanelOpen,
    setInfoPanelOpen,
    setSelectedStructure,
  } = useAnatomyStore();

  const structure = selectedStructureId ? getStructureById(selectedStructureId) : null;
  const content = selectedStructureId ? getContentForStructure(selectedStructureId) : null;

  if (!infoPanelOpen || !structure) return null;

  const displayName = viewMode === 'fitness'
    ? structure.commonName
    : structure.anatomicalName;

  return (
    <div className="absolute right-4 top-4 bottom-4 w-80 max-w-[calc(100vw-2rem)] overflow-hidden">
      <div className="h-full bg-surface-900/95 backdrop-blur-xl rounded-2xl border border-surface-700/50 shadow-2xl shadow-black/30 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-surface-700/50">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-semibold text-surface-100 truncate">
                {displayName}
              </h2>
              {viewMode === 'fitness' && structure.anatomicalName !== structure.commonName && (
                <p className="text-sm text-surface-400 truncate">
                  {structure.anatomicalName}
                </p>
              )}
              {viewMode === 'clinical' && structure.latinName && (
                <p className="text-sm text-surface-400 italic truncate">
                  {structure.latinName}
                </p>
              )}
            </div>
            <button
              onClick={() => {
                setInfoPanelOpen(false);
                setSelectedStructure(null);
              }}
              className="p-1.5 rounded-lg hover:bg-surface-800 transition-colors text-surface-400 hover:text-surface-200"
              aria-label="Close panel"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Type badge */}
          <span className={`
            inline-block mt-2 px-2 py-0.5 rounded text-xs uppercase tracking-wide font-medium
            ${structure.type === 'bone' ? 'bg-anatomy-bone/20 text-anatomy-bone' : ''}
            ${structure.type === 'muscle' ? 'bg-anatomy-muscle/20 text-red-300' : ''}
            ${structure.type === 'tendon' ? 'bg-anatomy-tendon/20 text-anatomy-tendon' : ''}
            ${structure.type === 'organ' ? 'bg-anatomy-organ/20 text-pink-300' : ''}
          `}>
            {structure.type}
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {content ? (
            <>
              {/* Description */}
              <section>
                <p className="text-sm text-surface-300 leading-relaxed">
                  {viewMode === 'fitness'
                    ? content.simpleDescription
                    : content.clinicalDescription
                  }
                </p>
              </section>

              {/* Muscle Details */}
              {content.muscleDetails && (
                <>
                  {/* Origin & Insertion */}
                  <section className="space-y-2">
                    <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
                      Attachments
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-surface-500">Origin: </span>
                        <span className="text-surface-300">
                          {content.muscleDetails.origin.join(', ')}
                        </span>
                      </div>
                      <div>
                        <span className="text-surface-500">Insertion: </span>
                        <span className="text-surface-300">
                          {content.muscleDetails.insertion.join(', ')}
                        </span>
                      </div>
                    </div>
                  </section>

                  {/* Actions */}
                  <section className="space-y-2">
                    <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
                      Actions
                    </h3>
                    <ul className="space-y-1">
                      {content.muscleDetails.actions.map((action, i) => (
                        <li key={i} className="text-sm text-surface-300 flex items-start gap-2">
                          <span className="text-surface-600 mt-1.5">•</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </section>

                  {/* Innervation (clinical mode) */}
                  {viewMode === 'clinical' && content.muscleDetails.innervation && (
                    <section className="space-y-2">
                      <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
                        Innervation
                      </h3>
                      <p className="text-sm text-surface-300">
                        {content.muscleDetails.innervation}
                      </p>
                    </section>
                  )}

                  {/* Fitness Notes (fitness mode) */}
                  {viewMode === 'fitness' && content.muscleDetails.fitnessNotes && (
                    <section className="space-y-2">
                      <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
                        Training Tips
                      </h3>
                      <p className="text-sm text-surface-300">
                        {content.muscleDetails.fitnessNotes}
                      </p>
                    </section>
                  )}

                  {/* Exercises */}
                  {content.muscleDetails.exercises && content.muscleDetails.exercises.length > 0 && (
                    <section className="space-y-2">
                      <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
                        Exercises
                      </h3>
                      <div className="flex flex-wrap gap-1.5">
                        {content.muscleDetails.exercises.map((exercise, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 text-xs bg-surface-800 text-surface-300 rounded-md"
                          >
                            {exercise}
                          </span>
                        ))}
                      </div>
                    </section>
                  )}
                </>
              )}

              {/* Clinical Relevance (clinical mode) */}
              {viewMode === 'clinical' && content.clinicalRelevance && (
                <section className="space-y-2">
                  <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
                    Clinical Relevance
                  </h3>
                  <p className="text-sm text-surface-300">
                    {content.clinicalRelevance}
                  </p>
                </section>
              )}

              {/* Related Structures */}
              {content.relatedStructures.length > 0 && (
                <section className="space-y-2">
                  <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
                    Related Structures
                  </h3>
                  <div className="flex flex-wrap gap-1.5">
                    {content.relatedStructures.map((relatedId) => {
                      const related = getStructureById(relatedId);
                      if (!related) return null;
                      return (
                        <button
                          key={relatedId}
                          onClick={() => setSelectedStructure(relatedId)}
                          className="px-2 py-1 text-xs bg-surface-800 hover:bg-surface-700 text-surface-300 rounded-md transition-colors"
                        >
                          {viewMode === 'fitness' ? related.commonName : related.anatomicalName}
                        </button>
                      );
                    })}
                  </div>
                </section>
              )}
            </>
          ) : (
            <p className="text-sm text-surface-500 italic">
              No detailed information available for this structure yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
