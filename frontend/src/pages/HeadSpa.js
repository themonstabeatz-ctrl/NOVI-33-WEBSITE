import React, { useEffect, useState, useRef } from "react";
import { Helmet } from "react-helmet";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import ParallaxCurvedSection from "../components/ParallaxCurvedSection";
import BenefitsParallaxSection from "../components/BenefitsParallaxSection";
import RefreshParallaxSection from "../components/RefreshParallaxSection";
import "./HeadSpa.css";

// Head Spa slike - žene i devojke (korisnikove slike)
const CARD_IMAGES = {
  headCare: "https://customer-assets.emergentagent.com/job_258640de-320b-4835-89c0-93d3d07cf337/artifacts/5tq0zb76_Behandelingen-Headspa-facial-1-2048x1151-1.jpg",
  headMassage: "https://customer-assets.emergentagent.com/job_258640de-320b-4835-89c0-93d3d07cf337/artifacts/3k9vkgli_vecteezy_head-massage-treatment-in-japanese-spa-with-skilled-hands-of_71594574.jpg",
  holisticSpa: "https://customer-assets.emergentagent.com/job_258640de-320b-4835-89c0-93d3d07cf337/artifacts/8n5qvvdv_vecteezy_closeup-of-woman-receiving-relaxing-facial-massage-therapy_75798882.jpeg",
  detox: "https://customer-assets.emergentagent.com/job_258640de-320b-4835-89c0-93d3d07cf337/artifacts/5pdxuokk_vecteezy_relaxing-hydromassage-session-featuring-a-woman-enjoying_71594435.jpg",
  relaxation: "https://customer-assets.emergentagent.com/job_258640de-320b-4835-89c0-93d3d07cf337/artifacts/t2pr9jtn_ezgi_149-scaled.jpg",
  premium: "https://images.pexels.com/photos/35176574/pexels-photo-35176574.jpeg?w=600"
};

// Head Spa content translations
const headSpaContent = {
  sr: {
    heroTitle: "Japanski Head Spa",
    heroSubtitle: "u Bua Luang Thai Spa",
    heroTagline: "Ritual koji budi temenje, neguje kosu i vraća mir u telo.",
    introTitle: "Više od nege kose",
    introText: "Bua Luang Head Spa je više od nege kose — to je luksuzni reset za vaše teme, vrat i um. Kombinujemo dubinsko čišćenje temena, parnu terapiju i preciznu masažu tačaka pritiska kako bismo smanjili napetost, osvežili kožu glave i podstakli zdrav rast kose. Namenjeno i ženama i muškarcima.",
    servicesTitle: "Naši tretmani",
    services: [
      {
        id: "head-care",
        image: CARD_IMAGES.headCare,
        title: "Head Care & Wash",
        price: "3.900 RSD",
        duration: "30 MIN",
        shortDesc: "Osvežavajuće pranje i nega temena sa premium šamponima.",
        fullDesc: "Tretman koji kombinuje dubinsko čišćenje temena sa premium šamponima i regenerativnu masažu. Uklanja nečistoće, višak sebuma i osvežava kožu glave. Idealno kao uvod u Head Spa ili za redovno održavanje."
      },
      {
        id: "head-massage",
        image: CARD_IMAGES.headMassage,
        title: "Head Massage",
        price: "4.500 RSD",
        duration: "45 MIN",
        shortDesc: "Relaksirajuća masaža temena za smanjenje stresa.",
        fullDesc: "Precizna masaža temena i vrata koja otpušta napetost, poboljšava cirkulaciju i smanjuje glavobolje. Koriste se tehnike pritiska na specifične tačke koje stimulišu opuštanje i mentalni reset."
      },
      {
        id: "holistic-spa",
        image: CARD_IMAGES.holisticSpa,
        title: "Holistic Head Spa",
        price: "7.800 RSD",
        duration: "60 MIN",
        shortDesc: "Kompletni tretman sa parom, maskom i masažom.",
        fullDesc: "Naš signature tretman koji uključuje dubinsko čišćenje, parnu terapiju, hranljivu masku i preciznu masažu tačaka pritiska. Rezultat: zdrava koža glave, sjajna kosa i potpuna relaksacija."
      },
      {
        id: "detox",
        image: CARD_IMAGES.detox,
        title: "Scalp Detox",
        price: "5.500 RSD",
        duration: "45 MIN",
        shortDesc: "Detoksikacija temena i uklanjanje naslaga.",
        fullDesc: "Specijalizovani tretman za detoksikaciju kože glave. Uklanja nakupljene naslage proizvoda, višak sebuma i nečistoće iz pora. Priprema teme za optimalnu apsorpciju hranljivih materija."
      },
      {
        id: "relaxation",
        image: CARD_IMAGES.relaxation,
        title: "Deep Relaxation",
        price: "6.500 RSD",
        duration: "60 MIN",
        shortDesc: "Duboka relaksacija sa aromaterapijom.",
        fullDesc: "Tretman fokusiran na maksimalnu relaksaciju. Kombinuje blagotvornu masažu sa aromaterapijom eteričnim uljima. Umiruje nervni sistem, poboljšava san i vraća balans umu i telu."
      },
      {
        id: "premium",
        image: CARD_IMAGES.premium,
        title: "Premium Head Spa",
        price: "9.900 RSD",
        duration: "90 MIN",
        shortDesc: "Luksuzni kompletni tretman sa svim dodacima.",
        fullDesc: "Naš najluksuzniji tretman koji uključuje sve: dubinsko čišćenje, parnu terapiju, premium masku, produženu masažu temena i vrata, aromaterapiju i završnu negu. Ultimativni Head Spa doživljaj."
      }
    ],
    processTitle: "Tok tretmana",
    processSteps: [
      "Masaža vrata, ramena i dekoltea",
      "Dubinsko čišćenje i blaga eksfolijacija temena",
      "Topla para (steam) za otvaranje pora i hidrataciju",
      "Maska + precizna masaža temena (pressure points)",
      "Završna nega kose — mekoća, sjaj i lako raščešljavanje"
    ],
    contraTitle: "Važno",
    contraText: "Tretman se ne preporučuje ako imate:",
    contraItems: [
      "Ekstenzije",
      "Sveže farbanje (može doći do blagog ispiranja boje)",
      "Aktivne infekcije ili iritacije temena",
      "Izrazito osetljivo teme",
      "Trudnoću",
      "Klaustrofobiju"
    ],
    ctaTitle: "Spremni za transformaciju?",
    ctaButton: "Zakažite Head Spa"
  },
  en: {
    heroTitle: "Japanese Head Spa",
    heroSubtitle: "at Bua Luang Thai Spa",
    heroTagline: "A ritual that awakens your scalp, nurtures your hair, and restores peace to your body.",
    introTitle: "More than hair care",
    introText: "Bua Luang Head Spa is more than hair care — it's a luxurious reset for your scalp, neck, and mind. We combine deep scalp cleansing, steam therapy, and precise pressure point massage to reduce tension, refresh your scalp, and promote healthy hair growth. For both women and men.",
    servicesTitle: "Our treatments",
    services: [
      {
        id: "head-care",
        image: CARD_IMAGES.headCare,
        title: "Head Care & Wash",
        price: "€35",
        duration: "30 MIN",
        shortDesc: "Refreshing wash and scalp care with premium shampoos.",
        fullDesc: "Treatment combining deep scalp cleansing with premium shampoos and regenerative massage. Removes impurities, excess sebum and refreshes the scalp. Ideal as an introduction to Head Spa or for regular maintenance."
      },
      {
        id: "head-massage",
        image: CARD_IMAGES.headMassage,
        title: "Head Massage",
        price: "€40",
        duration: "45 MIN",
        shortDesc: "Relaxing scalp massage to reduce stress.",
        fullDesc: "Precise scalp and neck massage that releases tension, improves circulation and reduces headaches. Pressure point techniques stimulate relaxation and mental reset."
      },
      {
        id: "holistic-spa",
        image: CARD_IMAGES.holisticSpa,
        title: "Holistic Head Spa",
        price: "€70",
        duration: "60 MIN",
        shortDesc: "Complete treatment with steam, mask and massage.",
        fullDesc: "Our signature treatment including deep cleansing, steam therapy, nourishing mask and precise pressure point massage. Result: healthy scalp, shiny hair and complete relaxation."
      },
      {
        id: "detox",
        image: CARD_IMAGES.detox,
        title: "Scalp Detox",
        price: "€50",
        duration: "45 MIN",
        shortDesc: "Scalp detoxification and buildup removal.",
        fullDesc: "Specialized treatment for scalp detoxification. Removes accumulated product buildup, excess sebum and pore impurities. Prepares scalp for optimal nutrient absorption."
      },
      {
        id: "relaxation",
        image: CARD_IMAGES.relaxation,
        title: "Deep Relaxation",
        price: "€60",
        duration: "60 MIN",
        shortDesc: "Deep relaxation with aromatherapy.",
        fullDesc: "Treatment focused on maximum relaxation. Combines soothing massage with essential oil aromatherapy. Calms the nervous system, improves sleep and restores balance."
      },
      {
        id: "premium",
        image: CARD_IMAGES.premium,
        title: "Premium Head Spa",
        price: "€90",
        duration: "90 MIN",
        shortDesc: "Luxurious complete treatment with all extras.",
        fullDesc: "Our most luxurious treatment including everything: deep cleansing, steam therapy, premium mask, extended scalp and neck massage, aromatherapy and finishing care. The ultimate Head Spa experience."
      }
    ],
    processTitle: "Treatment Process",
    processSteps: [
      "Neck, shoulder and décolleté massage",
      "Deep cleansing and gentle scalp exfoliation",
      "Warm steam for opening pores and hydration",
      "Mask + precise scalp massage (pressure points)",
      "Final hair care — softness, shine and easy detangling"
    ],
    contraTitle: "Important",
    contraText: "Treatment is not recommended if you have:",
    contraItems: [
      "Hair extensions",
      "Recent hair coloring (may cause slight color fading)",
      "Active scalp infections or irritations",
      "Extremely sensitive scalp",
      "Pregnancy",
      "Claustrophobia"
    ],
    ctaTitle: "Ready for transformation?",
    ctaButton: "Book Head Spa"
  },
  ru: {
    heroTitle: "Японский Head Spa",
    heroSubtitle: "в Bua Luang Thai Spa",
    heroTagline: "Ритуал, который пробуждает кожу головы, питает волосы и возвращает покой телу.",
    introTitle: "Больше, чем уход за волосами",
    introText: "Bua Luang Head Spa — это больше, чем уход за волосами — это роскошная перезагрузка для кожи головы, шеи и разума.",
    servicesTitle: "Наши процедуры",
    services: [
      {
        id: "head-care",
        image: CARD_IMAGES.headCare,
        title: "Head Care & Wash",
        price: "3.900 RSD",
        duration: "30 МИН",
        shortDesc: "Освежающее мытье и уход с премиальными шампунями.",
        fullDesc: "Процедура глубокого очищения кожи головы с премиальными шампунями и восстанавливающим массажем."
      },
      {
        id: "head-massage",
        image: CARD_IMAGES.headMassage,
        title: "Head Massage",
        price: "4.500 RSD",
        duration: "45 МИН",
        shortDesc: "Расслабляющий массаж для снятия стресса.",
        fullDesc: "Точный массаж кожи головы и шеи, снимающий напряжение и улучшающий кровообращение."
      },
      {
        id: "holistic-spa",
        image: CARD_IMAGES.holisticSpa,
        title: "Holistic Head Spa",
        price: "7.800 RSD",
        duration: "60 МИН",
        shortDesc: "Полная процедура с паром, маской и массажем.",
        fullDesc: "Наша фирменная процедура с глубоким очищением, паровой терапией и массажем точек давления."
      },
      {
        id: "detox",
        image: CARD_IMAGES.detox,
        title: "Scalp Detox",
        price: "5.500 RSD",
        duration: "45 МИН",
        shortDesc: "Детоксикация кожи головы.",
        fullDesc: "Специализированная процедура детоксикации кожи головы, удаляющая накопления и загрязнения."
      },
      {
        id: "relaxation",
        image: CARD_IMAGES.relaxation,
        title: "Deep Relaxation",
        price: "6.500 RSD",
        duration: "60 МИН",
        shortDesc: "Глубокое расслабление с ароматерапией.",
        fullDesc: "Процедура максимального расслабления с массажем и ароматерапией эфирными маслами."
      },
      {
        id: "premium",
        image: CARD_IMAGES.premium,
        title: "Premium Head Spa",
        price: "9.900 RSD",
        duration: "90 МИН",
        shortDesc: "Роскошная полная процедура.",
        fullDesc: "Наша самая роскошная процедура со всеми дополнениями: очищение, пар, маска, массаж и ароматерапия."
      }
    ],
    processTitle: "Процесс процедуры",
    processSteps: [
      "Массаж шеи, плеч и декольте",
      "Глубокое очищение и мягкий пилинг",
      "Теплый пар для открытия пор",
      "Маска + точечный массаж",
      "Финальный уход"
    ],
    contraTitle: "Важно",
    contraText: "Процедура не рекомендуется при:",
    contraItems: [
      "Наращенных волосах",
      "Недавнем окрашивании",
      "Активных инфекциях",
      "Очень чувствительной коже",
      "Беременности",
      "Клаустрофобии"
    ],
    ctaTitle: "Готовы к трансформации?",
    ctaButton: "Забронировать"
  },
  th: {
    heroTitle: "Japanese Head Spa",
    heroSubtitle: "ที่ Bua Luang Thai Spa",
    heroTagline: "พิธีกรรมที่ปลุกหนังศีรษะ บำรุงเส้นผม และคืนความสงบ",
    introTitle: "มากกว่าการดูแลผม",
    introText: "Bua Luang Head Spa เป็นมากกว่าการดูแลผม — เป็นการรีเซ็ตสุดหรูสำหรับหนังศีรษะ คอ และจิตใจ",
    servicesTitle: "การรักษาของเรา",
    services: [
      {
        id: "head-care",
        image: CARD_IMAGES.headCare,
        title: "Head Care & Wash",
        price: "฿1,200",
        duration: "30 นาที",
        shortDesc: "ล้างและดูแลด้วยแชมพูพรีเมียม",
        fullDesc: "การรักษาทำความสะอาดลึกด้วยแชมพูพรีเมียมและนวดฟื้นฟู"
      },
      {
        id: "head-massage",
        image: CARD_IMAGES.headMassage,
        title: "Head Massage",
        price: "฿1,400",
        duration: "45 นาที",
        shortDesc: "นวดผ่อนคลายเพื่อลดความเครียด",
        fullDesc: "นวดหนังศีรษะและคออย่างแม่นยำเพื่อคลายความตึงเครียด"
      },
      {
        id: "holistic-spa",
        image: CARD_IMAGES.holisticSpa,
        title: "Holistic Head Spa",
        price: "฿2,400",
        duration: "60 นาที",
        shortDesc: "การรักษาครบครันด้วยไอน้ำ มาส์ก และนวด",
        fullDesc: "การรักษาเอกลักษณ์ของเรารวมการทำความสะอาดลึก ไอน้ำ และนวดจุดกด"
      },
      {
        id: "detox",
        image: CARD_IMAGES.detox,
        title: "Scalp Detox",
        price: "฿1,700",
        duration: "45 นาที",
        shortDesc: "ดีท็อกซ์หนังศีรษะ",
        fullDesc: "การรักษาพิเศษสำหรับดีท็อกซ์หนังศีรษะ กำจัดสิ่งสะสมและสิ่งสกปรก"
      },
      {
        id: "relaxation",
        image: CARD_IMAGES.relaxation,
        title: "Deep Relaxation",
        price: "฿2,000",
        duration: "60 นาที",
        shortDesc: "ผ่อนคลายลึกด้วยอโรมาเธอราพี",
        fullDesc: "การรักษาผ่อนคลายสูงสุดกับนวดและอโรมาเธอราพี"
      },
      {
        id: "premium",
        image: CARD_IMAGES.premium,
        title: "Premium Head Spa",
        price: "฿3,000",
        duration: "90 นาที",
        shortDesc: "การรักษาหรูหราครบครัน",
        fullDesc: "การรักษาหรูหราที่สุดรวมทุกอย่าง: ทำความสะอาด ไอน้ำ มาส์ก นวด และอโรมาเธอราพี"
      }
    ],
    processTitle: "ขั้นตอนการรักษา",
    processSteps: [
      "นวดคอ ไหล่ และหน้าอก",
      "ทำความสะอาดลึกและขัดผิวอ่อนโยน",
      "ไอน้ำอุ่นเพื่อเปิดรูขุมขน",
      "มาส์ก + นวดจุดกด",
      "การดูแลขั้นสุดท้าย"
    ],
    contraTitle: "สำคัญ",
    contraText: "ไม่แนะนำการรักษาหากคุณมี:",
    contraItems: [
      "ต่อผม",
      "ทำสีผมเร็วๆ นี้",
      "การติดเชื้อ",
      "หนังศีรษะไวมาก",
      "การตั้งครรภ์",
      "กลัวที่แคบ"
    ],
    ctaTitle: "พร้อมสำหรับการเปลี่ยนแปลง?",
    ctaButton: "จอง"
  }
};

const HeadSpa = () => {
  const { currentLanguage } = useLanguage();
  const content = headSpaContent[currentLanguage] || headSpaContent.sr;
  const [isVisible, setIsVisible] = useState({});
  const [heroOpacity, setHeroOpacity] = useState(1);
  const [introVisible, setIntroVisible] = useState(false);
  const introRef = useRef(null);

  // Intersection Observer for animations
  useEffect(() => {
    const observerOptions = {
      threshold: 0.15,
      rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setIsVisible((prev) => ({ ...prev, [entry.target.id]: true }));
        }
      });
    }, observerOptions);

    const sections = document.querySelectorAll(".hs-animate");
    sections.forEach((section) => observer.observe(section));

    return () => observer.disconnect();
  }, []);

  // Intersection Observer za "Više od nege kose" sekciju - radi pri scroll gore i dole
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          // Postavlja true kad uđe, false kad izađe
          setIntroVisible(entry.isIntersecting);
        });
      },
      { threshold: 0.2 }
    );

    if (introRef.current) {
      observer.observe(introRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Hero fade out effect on scroll
  useEffect(() => {
    let rafId = null;

    const handleScroll = () => {
      if (rafId) return;
      
      rafId = requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        const opacity = Math.max(1 - (scrollY / 400), 0);
        setHeroOpacity(opacity);
        rafId = null;
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <>
      <Helmet>
        <title>Head Spa | Bua Luang Thai Spa</title>
        <meta name="description" content="Japanski Head Spa tretman - dubinsko čišćenje temena, parna terapija i masaža za zdraviju kosu i mentalni reset." />
      </Helmet>

      <div className="headspa-page">
        {/* HERO SECTION with Video Background */}
        <section className="hs-hero">
          <div className="hs-video-container">
            <video
              autoPlay
              muted
              loop
              playsInline
              preload="auto"
              className="hs-video"
            >
              <source 
                src="https://customer-assets.emergentagent.com/job_spa-multilingual/artifacts/vjbp3lam_headspa.mp4" 
                type="video/mp4" 
              />
            </video>
            <div className="hs-video-overlay"></div>
          </div>
          
          <div className="hs-hero-content" style={{ opacity: heroOpacity }}>
            <img 
              src="https://customer-assets.emergentagent.com/job_serene-retreat-1/artifacts/r2vm59ex_Bualuang%20logo%20senka.png" 
              alt="Bua Luang Thai Spa" 
              className="hs-hero-logo"
            />
            <h1 className="hs-hero-title">
              <span className="hs-title-main">{content.heroTitle}</span>
            </h1>
            <p className="hs-title-sub">{content.heroSubtitle}</p>
            <p className="hs-hero-tagline">{content.heroTagline}</p>
          </div>
        </section>

        {/* INTRO PARALLAX SECTION - "Više od nege kose" sa animacijom reči */}
        <section id="hs-intro-parallax" className="hs-intro-parallax" ref={introRef}>
          <div className="hs-intro-wave-top" aria-hidden="true"></div>
          <div className="hs-intro-wave-top-stroke" aria-hidden="true"></div>
          
          <div className={`hs-intro-content ${introVisible ? 'hs-intro-visible' : 'hs-intro-hidden'}`}>
            <h2 className="hs-intro-title">
              {content.introTitle.split(' ').map((word, index) => (
                <span 
                  key={index} 
                  className={`hs-word ${introVisible ? 'hs-word-visible' : ''}`}
                  style={{ animationDelay: `${index * 0.15}s` }}
                >
                  {word}&nbsp;
                </span>
              ))}
            </h2>
            <p className="hs-intro-text">
              {content.introText.split(' ').map((word, index) => (
                <span 
                  key={index} 
                  className={`hs-word ${introVisible ? 'hs-word-visible' : ''}`}
                  style={{ animationDelay: `${0.6 + index * 0.03}s` }}
                >
                  {word}&nbsp;
                </span>
              ))}
            </p>
          </div>
          
          <div className="hs-intro-wave-bottom" aria-hidden="true"></div>
          <div className="hs-intro-wave-bottom-stroke" aria-hidden="true"></div>
        </section>

        {/* NOVA PARALLAX SEKCIJA SA FLIP KARTICAMA */}
        <ParallaxCurvedSection 
          title={content.servicesTitle}
          cards={content.services}
        />

        {/* BENEFITS PARALLAX SEKCIJA - Nova sekcija sa istim stilom kao "Više od nege kose" */}
        <BenefitsParallaxSection lang={currentLanguage} />

        {/* REFRESH PARALLAX SEKCIJA - "Osvežite se" sa horizontalnim karticama */}
        <RefreshParallaxSection lang={currentLanguage} />

        {/* CONTRAINDICATIONS SECTION */}
        <section id="hs-contra" className="hs-section hs-contra hs-animate">
          <div className={`hs-container ${isVisible["hs-contra"] ? "hs-visible" : ""}`}>
            <h2 className="hs-section-title">{content.contraTitle}</h2>
            <p className="hs-contra-text">{content.contraText}</p>
            <ul className="hs-contra-list">
              {content.contraItems.map((item, index) => (
                <li 
                  key={index} 
                  className="hs-contra-item"
                  style={{ animationDelay: `${index * 0.08}s` }}
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* CTA SECTION */}
        <section id="hs-cta" className="hs-section hs-cta hs-animate">
          <div className={`hs-container ${isVisible["hs-cta"] ? "hs-visible" : ""}`}>
            <h2 className="hs-cta-title">{content.ctaTitle}</h2>
            <Link to="/contact" className="hs-cta-button" data-testid="head-spa-cta-button">
              {content.ctaButton}
            </Link>
          </div>
        </section>
      </div>
    </>
  );
};

export default HeadSpa;
