/* @ds-bundle: {"format":4,"namespace":"OurSecureFutureDesignSystem_3e86bd","components":[{"name":"Card","sourcePath":"components/data-display/Card.jsx"},{"name":"Badge","sourcePath":"components/feedback/Badge.jsx"},{"name":"Tag","sourcePath":"components/feedback/Tag.jsx"},{"name":"Button","sourcePath":"components/forms/Button.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Radio","sourcePath":"components/forms/Radio.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Tabs","sourcePath":"components/navigation/Tabs.jsx"},{"name":"BusinessCard","sourcePath":"ui_kits/stationery/BusinessCard.jsx"},{"name":"EmailSignature","sourcePath":"ui_kits/stationery/EmailSignature.jsx"},{"name":"Letterhead","sourcePath":"ui_kits/stationery/Letterhead.jsx"},{"name":"Hero","sourcePath":"ui_kits/website/Hero.jsx"},{"name":"SiteFooter","sourcePath":"ui_kits/website/SiteFooter.jsx"},{"name":"SiteHeader","sourcePath":"ui_kits/website/SiteHeader.jsx"}],"sourceHashes":{"components/data-display/Card.jsx":"4806b7978ea8","components/feedback/Badge.jsx":"8fd1b5d30319","components/feedback/Tag.jsx":"2d488da445eb","components/forms/Button.jsx":"429cef832087","components/forms/Checkbox.jsx":"44c821ab8c6d","components/forms/Input.jsx":"7175f52ef4ca","components/forms/Radio.jsx":"9650d810acbf","components/forms/Select.jsx":"34ae992b9e0b","components/navigation/Tabs.jsx":"c9381a58fe6e","ui_kits/stationery/BusinessCard.jsx":"ab2350f0a0e2","ui_kits/stationery/EmailSignature.jsx":"c03ad88ddf22","ui_kits/stationery/Letterhead.jsx":"156dc11a3e49","ui_kits/website/Hero.jsx":"4ff55b448013","ui_kits/website/SiteFooter.jsx":"e6b4f8987eef","ui_kits/website/SiteHeader.jsx":"e3860dd0cfe7"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.OurSecureFutureDesignSystem_3e86bd = window.OurSecureFutureDesignSystem_3e86bd || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/data-display/Card.jsx
try { (() => {
function Card({
  eyebrow,
  title,
  description,
  image,
  footer
}) {
  return React.createElement('div', {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-md)',
      overflow: 'hidden',
      boxShadow: 'var(--shadow-sm)',
      fontFamily: 'var(--font-sans)',
      display: 'flex',
      flexDirection: 'column'
    }
  }, image && React.createElement('div', {
    style: {
      height: 140,
      background: 'var(--surface-sunken)'
    }
  }, image), React.createElement('div', {
    style: {
      padding: 20,
      display: 'flex',
      flexDirection: 'column',
      gap: 8
    }
  }, eyebrow && React.createElement('div', {
    style: {
      fontSize: 'var(--fs-eyebrow)',
      letterSpacing: 'var(--ls-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--osf-teal-dark)',
      fontWeight: 'var(--fw-medium)'
    }
  }, eyebrow), title && React.createElement('div', {
    style: {
      fontFamily: 'var(--font-serif)',
      fontSize: 'var(--fs-h4)',
      color: 'var(--text-primary)'
    }
  }, title), description && React.createElement('div', {
    style: {
      fontSize: 14,
      color: 'var(--text-secondary)',
      lineHeight: 1.5
    }
  }, description), footer && React.createElement('div', {
    style: {
      marginTop: 8
    }
  }, footer)));
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data-display/Card.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Badge.jsx
try { (() => {
function Badge({
  children,
  tone = 'navy'
}) {
  const tones = {
    navy: {
      background: 'var(--osf-navy)',
      color: '#fff'
    },
    teal: {
      background: 'var(--osf-teal)',
      color: '#fff'
    },
    gold: {
      background: 'var(--osf-golden)',
      color: 'var(--osf-navy)'
    },
    sand: {
      background: 'var(--osf-sand)',
      color: 'var(--osf-navy)'
    }
  };
  return React.createElement('span', {
    style: {
      ...tones[tone],
      display: 'inline-flex',
      alignItems: 'center',
      padding: '4px 10px',
      borderRadius: 'var(--radius-pill)',
      fontFamily: 'var(--font-sans)',
      fontSize: 12,
      fontWeight: 'var(--fw-medium)',
      letterSpacing: '0.02em'
    }
  }, children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Badge.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Tag.jsx
try { (() => {
function Tag({
  children,
  onRemove
}) {
  return React.createElement('span', {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      padding: '4px 10px',
      borderRadius: 'var(--radius-sm)',
      background: 'var(--surface-sunken)',
      border: '1px solid var(--border-subtle)',
      fontFamily: 'var(--font-sans)',
      fontSize: 13,
      color: 'var(--text-primary)'
    }
  }, children, onRemove && React.createElement('button', {
    onClick: onRemove,
    style: {
      border: 'none',
      background: 'none',
      cursor: 'pointer',
      color: 'var(--text-muted)',
      fontSize: 14,
      lineHeight: 1,
      padding: 0
    }
  }, '×'));
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Tag.jsx", error: String((e && e.message) || e) }); }

// components/forms/Button.jsx
try { (() => {
function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  type = 'button'
}) {
  const base = {
    fontFamily: 'var(--font-sans)',
    fontWeight: 'var(--fw-medium)',
    border: '1px solid transparent',
    borderRadius: 'var(--radius-sm)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: 'background var(--duration-fast) var(--ease-standard), color var(--duration-fast) var(--ease-standard)',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    lineHeight: 1
  };
  const sizes = {
    sm: {
      padding: '8px 14px',
      fontSize: '14px'
    },
    md: {
      padding: '12px 22px',
      fontSize: '16px'
    },
    lg: {
      padding: '16px 28px',
      fontSize: '18px'
    }
  };
  const variants = {
    primary: {
      background: 'var(--color-primary)',
      color: '#fff',
      borderColor: 'var(--color-primary)'
    },
    accent: {
      background: 'var(--color-accent)',
      color: '#fff',
      borderColor: 'var(--color-accent)'
    },
    outline: {
      background: 'transparent',
      color: 'var(--color-primary)',
      borderColor: 'var(--color-primary)'
    },
    ghost: {
      background: 'transparent',
      color: 'var(--color-primary)',
      borderColor: 'transparent'
    },
    gold: {
      background: 'var(--color-gold)',
      color: 'var(--osf-navy)',
      borderColor: 'var(--color-gold)'
    }
  };
  return React.createElement('button', {
    type,
    disabled,
    onClick,
    style: {
      ...base,
      ...sizes[size],
      ...variants[variant]
    }
  }, children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Button.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function Checkbox({
  label,
  checked,
  onChange,
  disabled = false
}) {
  return React.createElement('label', {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      fontFamily: 'var(--font-sans)',
      fontSize: 15,
      color: 'var(--text-primary)',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.5 : 1
    }
  }, React.createElement('input', {
    type: 'checkbox',
    checked,
    disabled,
    onChange: e => onChange && onChange(e.target.checked),
    style: {
      width: 18,
      height: 18,
      accentColor: 'var(--osf-navy)'
    }
  }), label);
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function Input({
  label,
  placeholder,
  type = 'text',
  value,
  onChange,
  error,
  helpText,
  disabled = false
}) {
  return React.createElement('label', {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 6,
      fontFamily: 'var(--font-sans)',
      fontSize: 14,
      color: 'var(--text-primary)',
      width: '100%'
    }
  }, label && React.createElement('span', {
    style: {
      fontWeight: 'var(--fw-medium)'
    }
  }, label), React.createElement('input', {
    type,
    placeholder,
    value,
    disabled,
    onChange: e => onChange && onChange(e.target.value),
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 16,
      padding: '11px 14px',
      borderRadius: 'var(--radius-sm)',
      border: `1px solid ${error ? 'var(--color-danger)' : 'var(--border-subtle)'}`,
      background: disabled ? 'var(--surface-sunken)' : '#fff',
      color: 'var(--text-primary)',
      outline: 'none'
    }
  }), error ? React.createElement('span', {
    style: {
      color: 'var(--color-danger)',
      fontSize: 12
    }
  }, error) : helpText && React.createElement('span', {
    style: {
      color: 'var(--text-muted)',
      fontSize: 12
    }
  }, helpText));
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Radio.jsx
try { (() => {
function Radio({
  label,
  checked,
  onChange,
  name,
  disabled = false
}) {
  return React.createElement('label', {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      fontFamily: 'var(--font-sans)',
      fontSize: 15,
      color: 'var(--text-primary)',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.5 : 1
    }
  }, React.createElement('input', {
    type: 'radio',
    name,
    checked,
    disabled,
    onChange: e => onChange && onChange(e.target.checked),
    style: {
      width: 18,
      height: 18,
      accentColor: 'var(--osf-navy)'
    }
  }), label);
}
Object.assign(__ds_scope, { Radio });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Radio.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
function Select({
  label,
  options = [],
  value,
  onChange,
  disabled = false
}) {
  return React.createElement('label', {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 6,
      fontFamily: 'var(--font-sans)',
      fontSize: 14,
      color: 'var(--text-primary)',
      width: '100%'
    }
  }, label && React.createElement('span', {
    style: {
      fontWeight: 'var(--fw-medium)'
    }
  }, label), React.createElement('select', {
    value,
    disabled,
    onChange: e => onChange && onChange(e.target.value),
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 16,
      padding: '11px 14px',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--border-subtle)',
      background: disabled ? 'var(--surface-sunken)' : '#fff',
      color: 'var(--text-primary)'
    }
  }, options.map((o, i) => React.createElement('option', {
    key: i,
    value: o.value ?? o
  }, o.label ?? o))));
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tabs.jsx
try { (() => {
function Tabs({
  tabs = [],
  active,
  onChange
}) {
  return React.createElement('div', {
    style: {
      fontFamily: 'var(--font-sans)'
    }
  }, React.createElement('div', {
    style: {
      display: 'flex',
      gap: 4,
      borderBottom: '2px solid var(--border-subtle)'
    }
  }, tabs.map((t, i) => React.createElement('button', {
    key: i,
    onClick: () => onChange && onChange(t.value ?? t),
    style: {
      border: 'none',
      background: 'none',
      cursor: 'pointer',
      padding: '10px 16px',
      fontSize: 15,
      fontWeight: 'var(--fw-medium)',
      color: active === (t.value ?? t) ? 'var(--osf-navy)' : 'var(--text-muted)',
      borderBottom: active === (t.value ?? t) ? '2px solid var(--osf-teal)' : '2px solid transparent',
      marginBottom: -2
    }
  }, t.label ?? t))));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tabs.jsx", error: String((e && e.message) || e) }); }

// ui_kits/stationery/BusinessCard.jsx
try { (() => {
function BusinessCard({
  name,
  title,
  phone,
  email,
  web,
  address
}) {
  const face = {
    width: 336,
    height: 192,
    borderRadius: 8,
    boxShadow: 'var(--shadow-md)',
    fontFamily: 'var(--font-sans)',
    position: 'relative',
    overflow: 'hidden'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...face,
      background: '#fff',
      border: '1px solid var(--border-subtle)',
      padding: 20,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logos/OSF_Logo_Horizontal.jpg",
    style: {
      height: 28,
      width: 'fit-content'
    }
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontWeight: 600,
      color: 'var(--osf-navy)',
      fontSize: 15
    }
  }, name), /*#__PURE__*/React.createElement("div", {
    style: {
      color: 'var(--text-secondary)',
      fontSize: 12,
      marginBottom: 8
    }
  }, title), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-muted)',
      lineHeight: 1.6
    }
  }, phone, /*#__PURE__*/React.createElement("br", null), email, /*#__PURE__*/React.createElement("br", null), web))), /*#__PURE__*/React.createElement("div", {
    style: {
      ...face,
      background: 'var(--osf-navy)',
      padding: 20,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", null), /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logos/OSF_Logo_Marchio.jpg",
    style: {
      height: 70,
      filter: 'brightness(0) invert(1)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      color: '#fff',
      fontSize: 10,
      opacity: 0.8,
      textAlign: 'center'
    }
  }, address)));
}
Object.assign(__ds_scope, { BusinessCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/stationery/BusinessCard.jsx", error: String((e && e.message) || e) }); }

// ui_kits/stationery/EmailSignature.jsx
try { (() => {
function EmailSignature({
  name,
  pronouns,
  title,
  phone,
  web,
  address
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'Arial,Helvetica,sans-serif',
      fontSize: 13,
      color: '#274F66',
      display: 'flex',
      gap: 16,
      padding: 16,
      background: '#fff',
      border: '1px solid var(--border-subtle)',
      borderRadius: 8,
      width: 420
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logos/OSF_Logo_Marchio.jpg",
    style: {
      height: 48,
      width: 48
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderLeft: '2px solid #DBC45A',
      paddingLeft: 14,
      lineHeight: 1.5
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontWeight: 'bold'
    }
  }, name, " ", /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 'normal',
      color: '#5B5952'
    }
  }, "(", pronouns, ")")), /*#__PURE__*/React.createElement("div", {
    style: {
      color: '#5B5952'
    }
  }, title), /*#__PURE__*/React.createElement("div", {
    style: {
      color: '#5B5952'
    }
  }, "Our Secure Future | a program administered by PAX sapiens"), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 6
    }
  }, phone, /*#__PURE__*/React.createElement("br", null), web, /*#__PURE__*/React.createElement("br", null), address)));
}
Object.assign(__ds_scope, { EmailSignature });
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/stationery/EmailSignature.jsx", error: String((e && e.message) || e) }); }

// ui_kits/stationery/Letterhead.jsx
try { (() => {
function Letterhead({
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      width: 480,
      minHeight: 640,
      background: '#fff',
      boxShadow: 'var(--shadow-lg)',
      fontFamily: 'var(--font-sans)',
      padding: '32px 40px',
      display: 'flex',
      flexDirection: 'column'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      borderBottom: '2px solid var(--osf-teal)',
      paddingBottom: 16,
      marginBottom: 24
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logos/OSF_Logo_Horizontal.jpg",
    style: {
      height: 36
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 9,
      color: 'var(--text-muted)',
      textAlign: 'right',
      lineHeight: 1.6
    }
  }, "+1 303.555.1234", /*#__PURE__*/React.createElement("br", null), "oursecurefuture.org", /*#__PURE__*/React.createElement("br", null), "1501 M St NW, Suite 650, Washington, DC 20005")), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      color: 'var(--text-primary)',
      fontSize: 13,
      lineHeight: 1.7
    }
  }, children), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 9,
      color: 'var(--text-muted)',
      borderTop: '1px solid var(--border-subtle)',
      paddingTop: 10,
      marginTop: 16
    }
  }, "A program of PAX sapiens"));
}
Object.assign(__ds_scope, { Letterhead });
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/stationery/Letterhead.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/Hero.jsx
try { (() => {
function Hero() {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      background: 'var(--osf-navy)',
      color: '#fff',
      padding: '96px 48px',
      fontFamily: 'var(--font-sans)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      textAlign: 'center',
      gap: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-eyebrow)',
      letterSpacing: 'var(--ls-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--osf-golden)',
      fontWeight: 500
    }
  }, "Celebrating 10 Years — Est. 2016"), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-serif)',
      fontSize: 56,
      fontWeight: 500,
      maxWidth: 760,
      lineHeight: 1.15,
      margin: 0
    }
  }, "Women Make the Difference"), /*#__PURE__*/React.createElement("p", {
    style: {
      maxWidth: 600,
      fontSize: 18,
      color: 'rgba(255,255,255,0.85)',
      lineHeight: 1.6
    }
  }, "Advancing women's leadership and expertise in nuclear weapons policy — a program of PAX sapiens."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      marginTop: 12
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      background: 'var(--osf-golden)',
      color: 'var(--osf-navy)',
      padding: '14px 28px',
      borderRadius: 4,
      fontWeight: 600,
      textDecoration: 'none'
    }
  }, "Explore Our Work"), /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      border: '1px solid rgba(255,255,255,0.5)',
      color: '#fff',
      padding: '14px 28px',
      borderRadius: 4,
      fontWeight: 600,
      textDecoration: 'none'
    }
  }, "Get Involved")));
}
Object.assign(__ds_scope, { Hero });
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/Hero.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/SiteFooter.jsx
try { (() => {
function SiteFooter() {
  return /*#__PURE__*/React.createElement("footer", {
    style: {
      background: 'var(--gray-900)',
      color: 'rgba(255,255,255,0.7)',
      padding: '48px',
      fontFamily: 'var(--font-sans)',
      fontSize: 13,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logos/OSF_Logo_Marchio.jpg",
    style: {
      height: 32,
      filter: 'brightness(0) invert(1)'
    }
  }), /*#__PURE__*/React.createElement("span", null, "\xA9 2026 Our Secure Future — A program of PAX sapiens")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 24
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      color: 'inherit',
      textDecoration: 'none'
    }
  }, "Privacy"), /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      color: 'inherit',
      textDecoration: 'none'
    }
  }, "Contact"), /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      color: 'inherit',
      textDecoration: 'none'
    }
  }, "@OurSecureFuture")));
}
Object.assign(__ds_scope, { SiteFooter });
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/SiteFooter.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/SiteHeader.jsx
try { (() => {
function SiteHeader({
  active = 'Home'
}) {
  const links = ['Home', 'About', 'Research', 'Get Involved', 'News'];
  return /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '20px 48px',
      background: '#fff',
      borderBottom: '1px solid var(--border-subtle)',
      fontFamily: 'var(--font-sans)'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logos/OSF_Logo_Horizontal.jpg",
    style: {
      height: 40
    }
  }), /*#__PURE__*/React.createElement("nav", {
    style: {
      display: 'flex',
      gap: 32
    }
  }, links.map(l => /*#__PURE__*/React.createElement("a", {
    key: l,
    href: "#",
    style: {
      color: l === active ? 'var(--osf-navy)' : 'var(--text-secondary)',
      fontWeight: l === active ? 600 : 400,
      fontSize: 15,
      textDecoration: 'none',
      borderBottom: l === active ? '2px solid var(--osf-teal)' : '2px solid transparent',
      paddingBottom: 4
    }
  }, l))), /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      background: 'var(--osf-navy)',
      color: '#fff',
      padding: '10px 20px',
      borderRadius: 4,
      fontSize: 14,
      fontWeight: 500,
      textDecoration: 'none'
    }
  }, "Donate"));
}
Object.assign(__ds_scope, { SiteHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/SiteHeader.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Radio = __ds_scope.Radio;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Tabs = __ds_scope.Tabs;

__ds_ns.BusinessCard = __ds_scope.BusinessCard;

__ds_ns.EmailSignature = __ds_scope.EmailSignature;

__ds_ns.Letterhead = __ds_scope.Letterhead;

__ds_ns.Hero = __ds_scope.Hero;

__ds_ns.SiteFooter = __ds_scope.SiteFooter;

__ds_ns.SiteHeader = __ds_scope.SiteHeader;

})();
