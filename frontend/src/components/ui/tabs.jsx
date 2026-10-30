import * as React from "react"
import { cn } from "../../lib/utils"

const Tabs = ({ value, onValueChange, children, className }) => {
  return (
    <div className={cn("w-full", className)}>
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) return child
        return React.cloneElement(child, { activeValue: value, onValueChange })
      })}
    </div>
  )
}

const TabsList = ({ className, activeValue, onValueChange, children, ...props }) => {
  return (
    <div
      className={cn(
        "inline-flex h-11 items-center justify-start rounded-xl bg-slate-900/80 p-1 text-slate-400 border border-slate-800 gap-1",
        className
      )}
      {...props}
    >
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) return child
        return React.cloneElement(child, {
          isActive: child.props.value === activeValue,
          onClick: () => onValueChange && onValueChange(child.props.value),
        })
      })}
    </div>
  )
}

const TabsTrigger = ({ className, value, isActive, onClick, children, ...props }) => {
  return (
    <button
      type="button"
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 disabled:pointer-events-none disabled:opacity-50 select-none gap-2",
        isActive
          ? "bg-slate-800 text-emerald-400 shadow-md font-semibold border border-slate-700/80"
          : "hover:bg-slate-850 hover:text-slate-200 text-slate-400",
        className
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  )
}

const TabsContent = ({ value, activeValue, className, children, ...props }) => {
  if (value !== activeValue) return null
  return (
    <div
      className={cn(
        "mt-4 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 animate-in fade-in-50 duration-200",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export { Tabs, TabsList, TabsTrigger, TabsContent }
