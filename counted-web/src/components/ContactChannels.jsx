import { formatPhone } from '../lib/formatPhone';

function PhoneLink({ raw, className, children }) {
  const phone = formatPhone(raw);
  if (!phone) return null;
  return (
    <a href={phone.tel} className={className}>
      {children || phone.display}
    </a>
  );
}

export default function ContactChannels({ contact }) {
  const dcPhone = formatPhone(contact.dc_phone);
  const stateOffices = contact.state_offices || [];
  const social = contact.social || {};

  return (
    <div className="space-y-4">
      {/* DC Phone -- primary CTA */}
      {dcPhone && (
        <a
          href={dcPhone.tel}
          className="block w-full bg-amber hover:bg-amber-dark text-white text-center font-semibold py-4 px-6 rounded-lg text-lg transition-colors"
        >
          Call DC Office: {dcPhone.display}
        </a>
      )}

      {/* State offices */}
      {stateOffices.length > 0 && (
        <div>
          <h4 className="text-navy font-medium text-sm mb-2">State Offices</h4>
          <ul className="space-y-1">
            {stateOffices.map((office) => {
              const phone = formatPhone(office.phone);
              return (
                <li key={office.city || office.phone}>
                  {phone ? (
                    <a
                      href={phone.tel}
                      className="text-navy hover:text-amber-dark text-sm"
                    >
                      {office.city}: {phone.display}
                    </a>
                  ) : (
                    <span className="text-sm text-gray-600">{office.city}</span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {/* Web contact form */}
      {contact.web_form_url && (
        <div>
          <h4 className="text-navy font-medium text-sm mb-1">Contact Form</h4>
          <a
            href={contact.web_form_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-navy hover:text-amber-dark underline"
          >
            Submit via web form
          </a>
        </div>
      )}

      {/* Social media */}
      {social.twitter && (
        <div>
          <h4 className="text-navy font-medium text-sm mb-1">Social Media</h4>
          <a
            href={`https://twitter.com/${social.twitter.replace(/^@/, '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-navy hover:text-amber-dark"
          >
            {social.twitter}
          </a>
        </div>
      )}

      {/* Fax */}
      {contact.dc_fax && (
        <div>
          <h4 className="text-navy font-medium text-sm mb-1">Fax</h4>
          <PhoneLink raw={contact.dc_fax} className="text-sm text-gray-600 hover:text-navy" />
        </div>
      )}
    </div>
  );
}
