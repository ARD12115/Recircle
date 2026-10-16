import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { useAuthStore } from '../stores/ui'

const FEATURES = [
  {
    title: 'Scan with context',
    description: 'Start with a photo and a campus source, then confirm the bin you actually used.',
    style: 'feature-card-primary',
    mark: '01',
  },
  {
    title: 'Trace the flow',
    description: 'See confirmed disposal choices move through the campus digital twin.',
    style: 'feature-card-green',
    mark: '02',
  },
  {
    title: 'Test a change',
    description: 'Compare a collection scenario before changing a real campus operation.',
    style: 'feature-card-warm',
    mark: '03',
  },
]

const TECHNOLOGIES = [
  'React',
  'TypeScript',
  'FastAPI',
  'Computer vision',
  'Digital twin',
  'Scenario simulation',
]

export function Landing() {
  const navigate = useNavigate()
  const { isDemo } = useAuthStore()

  const openDemo = (path: string) => {
    navigate(`/login?mode=demo&next=${encodeURIComponent(path)}`)
  }

  return (
    <div className="space-y-20 pb-8 sm:space-y-24">
      <section className="grid items-center gap-10 py-5 lg:grid-cols-[0.92fr_1.08fr] lg:gap-14">
        <div className="max-w-2xl">
          <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-primary-300 bg-primary-50 px-4 py-2 text-xs font-bold uppercase tracking-[0.14em] text-primary-900">
            <span className="font-black" aria-hidden="true">RC /</span>
            Campus circularity, made visible
          </p>
          <h1 className="mb-6 text-5xl font-black leading-[0.94] tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
            Make waste
            <br />
            make sense.
          </h1>
          <p className="mb-8 max-w-xl text-lg leading-relaxed text-gray-600 sm:text-xl">
            Connect item scans, confirmed bins, and a living view of campus waste flows.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button size="lg" onClick={() => openDemo('/scan')} className="w-full sm:w-auto">
              Try a demo scan
            </Button>
            <Button variant="secondary" size="lg" onClick={() => openDemo('/twin')} className="w-full sm:w-auto">
              Explore the twin
            </Button>
          </div>
        </div>

        <figure className="hero-art">
          <img
            className="hero-photo"
            src="https://picsum.photos/seed/recircle-campus-circularity/1400/1100"
            alt="Colorful reusable and recyclable materials arranged in a circular composition"
            width="1400"
            height="1100"
            fetchPriority="high"
          />
          <figcaption className="hero-caption">
            <span className="text-xs font-bold uppercase tracking-[0.16em] text-lime-200">One campus. Many loops.</span>
            <span className="mt-2 block max-w-sm text-2xl font-black leading-tight text-white sm:text-3xl">
              Follow an item beyond the bin.
            </span>
          </figcaption>
        </figure>
      </section>

      {isDemo && (
        <div className="rounded-2xl border border-amber-300 bg-amber-50 px-5 py-4 text-amber-900" role="status">
          <p className="font-semibold">Demo mode is active. Campus measurements are simulated.</p>
        </div>
      )}

      <section aria-labelledby="features-title">
        <div className="mb-8 max-w-2xl">
          <h2 id="features-title" className="mb-3 text-3xl font-black text-gray-900 sm:text-4xl">
            From a single item to a system view.
          </h2>
          <p className="text-gray-600">
            ReCircle connects everyday sorting choices with campus-level decisions.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-[1.2fr_1fr_1fr]">
          {FEATURES.map(feature => (
            <Card key={feature.title} className={`feature-card ${feature.style}`}>
              <div className="mb-8 flex items-center justify-between">
                <span className="step-number" aria-hidden="true">{feature.mark}</span>
                <span className="text-xs font-bold uppercase tracking-[0.14em] opacity-80">ReCircle</span>
              </div>
              <h3 className="mb-2 text-2xl font-black">{feature.title}</h3>
              <p className="max-w-sm leading-relaxed opacity-85">{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.78fr_1.22fr]" aria-labelledby="process-title">
        <div className="max-w-lg">
          <h2 id="process-title" className="mb-4 text-3xl font-black sm:text-4xl">
            A clear path through the waste stream.
          </h2>
          <p className="leading-relaxed text-gray-600">
            Every confirmed choice adds evidence. The twin and recommendations stay grounded in what the demo has recorded.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            ['Scan', 'Choose a campus source and photograph an item.'],
            ['Confirm', 'Tell the system which bin received it.'],
            ['Measure', 'Review the updated flow and test alternatives.'],
          ].map(([title, description], index) => (
            <div key={title} className="process-step">
              <span className="process-step-number" aria-hidden="true">0{index + 1}</span>
              <h3 className="mb-2 text-xl font-black">{title}</h3>
              <p className="text-sm leading-relaxed text-gray-600">{description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="technology-band" aria-labelledby="technology-title">
        <h2 id="technology-title" className="mb-5 text-2xl font-black">Built to connect the loop</h2>
        <div className="flex flex-wrap gap-2">
          {TECHNOLOGIES.map(technology => (
            <span key={technology} className="technology-chip">{technology}</span>
          ))}
        </div>
      </section>
    </div>
  )
}
