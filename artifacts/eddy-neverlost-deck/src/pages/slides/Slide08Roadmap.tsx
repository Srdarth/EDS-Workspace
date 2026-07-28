export default function Slide08Roadmap() {
  return (
    <div className="bp-slide">
      <div className="bp-frame" />
      <div className="bp-frame-inner" />
      <div className="bp-content">
        <div className="bp-section">
          <div>
            <div className="bp-meta">Section 08</div>
            <div className="bp-code">DELIVERY / VERSION PATH</div>
          </div>
          <div className="bp-ref">
            <div className="bp-meta">Ref No.</div>
            <div className="bp-ref-value">RDM-08X</div>
          </div>
        </div>
        <div className="bp-body">
          <h1 className="bp-section-title">Roadmap: do diagnóstico ao sistema operacional</h1>
          <div className="bp-roadmap">
            <div className="bp-roadmap-cell"><div className="bp-roadmap-code">V0</div><p className="bp-roadmap-copy">Ambiente, Git, Docker e banco</p></div>
            <div className="bp-roadmap-cell"><div className="bp-roadmap-code">V1</div><p className="bp-roadmap-copy">NeverLost-lite com scanner e dashboard</p></div>
            <div className="bp-roadmap-cell"><div className="bp-roadmap-code">V2</div><p className="bp-roadmap-copy">Armazenamento e indexação</p></div>
            <div className="bp-roadmap-cell"><div className="bp-roadmap-code">V3–V4</div><p className="bp-roadmap-copy">Resumos, prompts e geração de conteúdo</p></div>
            <div className="bp-roadmap-cell"><div className="bp-roadmap-code">V5</div><p className="bp-roadmap-copy">Automações com n8n</p></div>
            <div className="bp-roadmap-cell"><div className="bp-roadmap-code">V6</div><p className="bp-roadmap-copy">Interface e gestão de usuários</p></div>
            <div className="bp-roadmap-cell"><div className="bp-roadmap-code">V7</div><p className="bp-roadmap-copy">SaaS inicial, cobrança e início das vendas</p></div>
          </div>
        </div>
        <div className="bp-footer">
          <div className="bp-footer-cell"><div className="bp-footer-label">Delivery Mode</div><div className="bp-footer-value">INCREMENTAL</div></div>
          <div className="bp-footer-cell"><div className="bp-footer-label">Page</div><div className="bp-footer-value">08 / 09</div></div>
          <div className="bp-footer-cell"><div className="bp-footer-label">Current</div><div className="bp-footer-value">V1 / MVP</div></div>
        </div>
      </div>
    </div>
  );
}