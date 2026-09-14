import { ReactNode } from 'react'

/**
 * A page with no rows should say why it is empty, not render a blank card.
 * A brand-new account is exactly this case, so it is the first thing anyone
 * sees after registering.
 */
export default function EmptyState({ title, hint }: { title: string; hint?: ReactNode }) {
  return (
    <div className="px-6 py-12 text-center">
      <p className="text-sm font-medium text-gray-900">{title}</p>
      {hint && <p className="mt-1 text-sm text-gray-500">{hint}</p>}
    </div>
  )
}
