import React from 'react';
import { ModulePlaceholder } from '../components/common/ModulePlaceholder';

export const ProductMisplacementPage: React.FC = () => {
  return (
    <ModulePlaceholder
      title="Product Misplacement & Planogram Compliance"
      stage="Stage 7"
      category="Computer Vision & Store Operations"
      description="Computer vision audit engine comparing physical shelf detections against official digital planograms to immediately flag misplaced, hidden, or inverted merchandise."
      objectives={[
        'Detect items placed on wrong shelves or adjacent product facings',
        'Compare bounding box classifications with planogram SKU layout tables',
        'Calculate store-wide planogram compliance and visual facing score',
        'Issue corrective replenishment tasks to floor staff mobile devices',
      ]}
      inputs={[
        'High-resolution shelf camera images & detected bounding boxes',
        'Grocery Store Dataset fine-grained classification models',
        'Digital store planograms and facing allocation blueprints',
      ]}
      outputs={[
        'Visual overlay highlighting misplaced items with red bounding boxes',
        'Planogram compliance score breakdown by aisle and category',
        'Floor correction task queue with exact shelf coordinates',
      ]}
      badgeColor="bg-rose-100 text-rose-800 border-rose-300"
    />
  );
};
