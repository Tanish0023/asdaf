import * as React from "react"
import { cva } from "class-variance-authority"
import { cn } from "../../lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-slate-800 text-slate-100 hover:bg-slate-700",
        secondary:
          "border-transparent bg-slate-850 text-slate-300 hover:bg-slate-800",
        destructive:
          "border-transparent bg-rose-500/20 text-rose-300 border-rose-500/30",
        outline: "text-slate-300 border-slate-700",
        success:
          "border-emerald-500/30 bg-emerald-500/15 text-emerald-300",
        warning:
          "border-amber-500/30 bg-amber-500/15 text-amber-300",
        info:
          "border-sky-500/30 bg-sky-500/15 text-sky-300",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({ className, variant, ...props }) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
