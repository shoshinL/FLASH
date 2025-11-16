/**
 * Reusable Loading Skeleton Component
 */

import { SKELETON } from "../../config";

interface LoadingSkeletonProps {
  type?: 'title' | 'text' | 'select' | 'input' | 'button' | 'section';
  width?: string;
  height?: string;
  style?: React.CSSProperties;
}

export function LoadingSkeleton({
  type = 'text',
  width,
  height,
  style = {}
}: LoadingSkeletonProps) {
  const getClassName = () => {
    switch (type) {
      case 'title':
        return 'skeleton skeleton-title';
      case 'select':
        return 'skeleton skeleton-select';
      case 'input':
        return 'skeleton skeleton-input';
      case 'button':
        return 'skeleton skeleton-button';
      case 'section':
        return 'skeleton-section';
      default:
        return 'skeleton skeleton-text';
    }
  };

  const combinedStyle: React.CSSProperties = {
    ...style,
    ...(width && { width }),
    ...(height && { height })
  };

  return <div className={getClassName()} style={combinedStyle}></div>;
}

/**
 * Full Page Loading Skeleton
 */
export function SettingsLoadingSkeleton() {
  return (
    <div className="provider-settings-container">
      <LoadingSkeleton type="title" />
      <div className="skeleton-section">
        <LoadingSkeleton type="text" width={SKELETON.TEXT_WIDTH_PRIMARY} style={{ marginBottom: '10px' }} />
        <LoadingSkeleton type="select" />
      </div>
      <div className="skeleton-section">
        <LoadingSkeleton type="text" width={SKELETON.TEXT_WIDTH_SECONDARY} style={{ marginBottom: '10px' }} />
        <LoadingSkeleton type="select" />
      </div>
      <div className="skeleton-section">
        <LoadingSkeleton type="button" />
      </div>
    </div>
  );
}
