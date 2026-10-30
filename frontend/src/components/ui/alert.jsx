import * as React from "react"
import { cva } from "class-variance-authority"
import { cn } from "../../lib/utils"

const alertVariants = cva(
  "relative w-full rounded-xl border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground",
  {
    variants: {
      variant: {
        default: "bg-slate-900 border-slate-800 text-slate-100",
        destructive:
          "border-rose-500/50 text-rose-300 dark:border-rose-500 [&>svg]:text-rose-400 bg-rose-950/20",
        success:
          "border-emerald-500/50 text-emerald-300 dark:border-emerald-500 [&>svg]:text-emerald-400 bg-emerald-950/20",
        warning:
          "border-amber-500/50 text-amber-300 dark:border-amber-500 [&>svg]:text-amber-400 bg-amber-950/20",
        info:
          "border-sky-500/50 text-sky-300 dark:border-sky-500 [&>svg]:text-sky-400 bg-sky-950/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const Alert = React.forwardRef(({ className, variant, ...props }, ref) => (
  <div
    ref={ref}
    role="alert"
    className={cn(alertVariants({ variant }), className)}
    {...props}
  />
))
Alert.displayName = "Alert"

const AlertTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("mb-1 font-semibold leading-none tracking-tight text-white", className)}
    {...props}
  />
))
AlertTitle.displayName = "AlertTitle"

const AlertDescription = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-xs [&_p]:leading-relaxed text-slate-300", className)}
    {...props}
  />
))
AlertDescription.displayName = "AlertDescription"

export { Alert, AlertTitle, AlertDescription }
