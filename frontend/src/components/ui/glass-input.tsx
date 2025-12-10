/**
 * Glass Input Component
 * ---------------------
 * Modern glassmorphism input field.
 */

import { cn } from "@/lib/utils";
import React from "react";

export interface GlassInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
  rightElement?: React.ReactNode;
  label?: string;
}

const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, icon, rightElement, label, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="text-xs text-muted font-medium mb-1.5 block pl-3">
            {label}
          </label>
        )}
        <div className={cn("glass-input-wrap w-full", className)}>
          <div className="glass-input">
            <span className="glass-input-text-area"></span>
            {icon && (
              <div className="relative z-10 flex-shrink-0 flex items-center justify-center w-10 pl-2 text-primary/70">
                {icon}
              </div>
            )}
            <input
              ref={ref}
              className={cn(
                "relative z-10 h-full w-0 flex-grow bg-transparent text-primary placeholder:text-primary/50 focus:outline-none py-3",
                !icon && "pl-4"
              )}
              {...props}
            />
            {rightElement && (
              <div className="relative z-10 flex-shrink-0 pr-2">
                {rightElement}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
);

GlassInput.displayName = "GlassInput";
export { GlassInput };
