import React, { useState, useEffect } from "react";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { useToast } from "../hooks/use-toast";
import { Mail, Phone, MapPin, Clock, Instagram, Send, X, Calendar } from "lucide-react";
import { useLocation } from "react-router-dom";
import CustomCalendarModal from "../components/CustomCalendarModal";
import CustomTimePickerModal from "../components/CustomTimePickerModal";
import { massageServices, spaServices, durations, bookingSystemNames } from "../data/servicesList";
import "react-datepicker/dist/react-datepicker.css";

const Contact = () => {
  const { translate, language } = useLanguage();
  const { toast } = useToast();
  const location = useLocation();
  
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    phone: "",
    email: "",
    message: "",
    preferredDate: null, // Changed to null for DatePicker
    preferredTime: "",
    source: "message" // 'booking', 'voucher', or 'message'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' or 'error'

  // Map language codes to HTML lang attribute - force sr-RS for date format
  const getHtmlLang = () => {
    // Always use sr-RS for Serbian date format (DD.MM.YYYY)
    return 'sr-RS';
  };

  // Set HTML lang attribute for native date picker localization
  useEffect(() => {
    document.documentElement.lang = getHtmlLang();
  }, [language]);

  // Scroll to top when component mounts and check for service parameter
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Get service parameter from URL
    const searchParams = new URLSearchParams(location.search);
    const service = searchParams.get('service');
    const source = searchParams.get('source'); // 'voucher', 'massage', 'spa', or null
    const couplesData = searchParams.get('couplesData');
    
    if (service) {
      let message = `Izabrali ste ${service}`;
      
      // Special handling for couples massage
      if (couplesData) {
        try {
          const data = JSON.parse(decodeURIComponent(couplesData));
          // Use totalDuration (sum of all massages) instead of duration (category)
          const displayDuration = data.totalDuration || data.duration;
          message = `Masaža za parove - UKUPNO TRAJANJE: ${displayDuration} min\n\n`;
          message += `OSOBA 1:\n`;
          if (data.person1.massage1) {
            message += `- ${data.person1.massage1.name} (${data.person1.massage1.duration} min) - ${data.person1.massage1.price} RSD\n`;
          }
          if (data.person1.massage2) {
            message += `- ${data.person1.massage2.name} (${data.person1.massage2.duration} min) - ${data.person1.massage2.price} RSD\n`;
          }
          message += `\nOSOBA 2:\n`;
          if (data.person2.massage1) {
            message += `- ${data.person2.massage1.name} (${data.person2.massage1.duration} min) - ${data.person2.massage1.price} RSD\n`;
          }
          if (data.person2.massage2) {
            message += `- ${data.person2.massage2.name} (${data.person2.massage2.duration} min) - ${data.person2.massage2.price} RSD\n`;
          }
          message += `\nPOPUST: -${data.discount}\n`;
          message += `UKUPNA CENA SA POPUSTOM: ${data.totalPrice.toLocaleString()} RSD`;
        } catch (e) {
          console.error('Error parsing couples data:', e);
        }
      }
      
      setFormData(prev => ({
        ...prev,
        message: message,
        source: source || 'booking' // Store source for success message
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        source: source || 'message' // Default to message if no service
      }));
    }
  }, [location, translate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle date change from DatePicker
  const handleDateChange = (date) => {
    setFormData(prev => ({
      ...prev,
      preferredDate: date
    }));
  };

  const clearDate = () => {
    setFormData(prev => ({
      ...prev,
      preferredDate: null
    }));
  };

  const clearTime = () => {
    setFormData(prev => ({
      ...prev,
      preferredTime: ""
    }));
  };

  // Format date for display as DD/MM/YYYY
  const formatDateForDisplay = (isoDate) => {
    if (!isoDate) return '';
    const [year, month, day] = isoDate.split('-');
    return `${day}/${month}/${year}`;
  };

  // Format date as DD/MM/YYYY
  const formatDate = (dateString) => {
    if (!dateString) return 'Nije navedeno';
    const date = new Date(dateString + 'T00:00:00');
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);
    
    try {
      // Validate required fields with detailed error messages
      const missingFields = [];
      
      if (!formData.firstName) missingFields.push('firstName');
      if (!formData.lastName) missingFields.push('lastName');
      if (!formData.phone) missingFields.push('phone');
      if (!formData.email) missingFields.push('email');
      
      // Check if this is a booking (has service parameter)
      const queryParams = new URLSearchParams(location.search);
      const serviceName = queryParams.get('service') || formData.service || '';
      const isBooking = !!serviceName;
      
      // For bookings, date and time are required
      if (isBooking) {
        if (!formData.preferredDate) missingFields.push('date');
        if (!formData.preferredTime) missingFields.push('time');
      }
      
      // If there are missing fields, show error and scroll to first missing field
      if (missingFields.length > 0) {
        // Create error message based on missing fields
        let errorMessage = translate('fillAllFields') || 'Molimo popunite sva obavezna polja: ';
        const fieldNames = {
          firstName: translate('firstName') || 'Ime',
          lastName: translate('lastName') || 'Prezime',
          phone: translate('phone') || 'Telefon',
          email: translate('email') || 'Email',
          date: translate('selectDate') || 'Datum',
          time: translate('selectTime') || 'Vreme'
        };
        
        const missingFieldNames = missingFields.map(field => fieldNames[field]);
        errorMessage += missingFieldNames.join(', ');
        
        // Show error toast
        toast({
          title: translate('error') || 'Greška',
          description: errorMessage,
          variant: "destructive",
        });
        
        // Scroll to first missing field
        const firstMissingField = missingFields[0];
        let fieldElement = null;
        
        if (firstMissingField === 'date') {
          fieldElement = document.querySelector('.calendar-input-trigger');
        } else if (firstMissingField === 'time') {
          fieldElement = document.querySelector('.time-input-trigger');
        } else {
          fieldElement = document.querySelector(`input[name="${firstMissingField}"]`);
        }
        
        if (fieldElement) {
          fieldElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          // Add visual indication (red border)
          fieldElement.style.border = '2px solid #dc2626';
          fieldElement.style.animation = 'shake 0.5s';
          
          // Remove red border after 3 seconds
          setTimeout(() => {
            fieldElement.style.border = '';
            fieldElement.style.animation = '';
          }, 3000);
        }
        
        setIsSubmitting(false);
        return;
      }
      
      // serviceName and queryParams already defined in validation above - no need to redeclare
      
      // Special handling for "Masaža za parove" - use original duration for service_id lookup
      let serviceLookupName = serviceName;
      const couplesDataParam = queryParams.get('couplesData');
      
      console.log('🔍 DEBUG - serviceName:', serviceName);
      console.log('🔍 DEBUG - couplesDataParam exists:', !!couplesDataParam);
      
      if (couplesDataParam && serviceName.includes('Masaža za parove')) {
        try {
          const couplesData = JSON.parse(decodeURIComponent(couplesDataParam));
          console.log('🔍 DEBUG - couplesData:', couplesData);
          console.log('🔍 DEBUG - couplesData.duration:', couplesData.duration);
          
          // Use original duration (60, 90, 120) for service_id lookup, not total duration
          serviceLookupName = `Masaža za parove - ${couplesData.duration} min`;
          console.log('🔄 Couples massage: using duration', couplesData.duration, 'for service lookup instead of total', couplesData.totalDuration);
          console.log('🔍 DEBUG - serviceLookupName:', serviceLookupName);
        } catch (e) {
          console.error('❌ Error parsing couples data for service lookup:', e);
        }
      }
      
      // Service Mapping - All 90 services with proper durations (30 types x 3 durations)
      const serviceMapping = {
        "Anti-age tretman - 120 min": "8ee6b874-4b3e-4981-a69f-0eeb50bc31bd",
        "Anti-age tretman - 60 min": "f335f1f3-c16f-4c11-bca3-08e4d0bd0484",
        "Anti-age tretman - 90 min": "855ca3d1-a03b-4dc4-b24a-77f97e8f594e",
        "Anticelulit tretman - 120 min": "39ada4f4-393c-4db2-9b20-8a9068639611",
        "Anticelulit tretman - 60 min": "abae009f-abda-4a5b-b1d3-6f11cb31c25e",
        "Anticelulit tretman - 90 min": "4f50ee14-1f6f-4383-b425-6e087e1bdf64",
        "Antistres masaža - 120 min": "bf892ffc-52d3-4344-95ef-28ed56ca3328",
        "Antistres masaža - 60 min": "720b91c4-acef-45de-ac87-ed95f5f9f1a3",
        "Antistres masaža - 90 min": "831c0549-c02b-4509-ace8-f59ee650cf60",
        "Aroma terapija - 120 min": "aabed0b8-798b-413f-8874-138c8c2b9c7c",
        "Aroma terapija - 60 min": "f81ee187-1d45-4942-abf3-4b83f147bf85",
        "Aroma terapija - 90 min": "006d97e0-409d-4d85-966e-99aacc908510",
        "Bamboo masaža - 120 min": "0df5d540-2493-457c-93db-5efbd10363ea",
        "Bamboo masaža - 60 min": "aef91adc-0cdf-4edf-824c-5b55931fae37",
        "Bamboo masaža - 90 min": "d16995bb-4719-42b8-9fd1-f472e744b3a2",
        "Body wrap - 120 min": "48af7be0-98f5-4594-80e1-51bb6ea8d081",
        "Body wrap - 60 min": "945b4e8a-bdda-4fc4-bd0c-5990be9e291b",
        "Body wrap - 90 min": "46499099-253f-4666-9122-1de3a64bf78e",
        "Detox tretman - 120 min": "71835956-0766-4db8-8ffd-bac47e79d283",
        "Detox tretman - 60 min": "9d29cdaf-6cca-4ed2-a2f1-43f8bc5341b0",
        "Detox tretman - 90 min": "58324e77-2523-43b2-9a30-4f029056b6ed",
        "Hidratantni tretman - 120 min": "6ffd4cca-bd0d-4a48-9c87-f2c0f14af8e1",
        "Hidratantni tretman - 60 min": "098f9bdc-9e18-4840-98b0-80ce32ca7d5a",
        "Hidratantni tretman - 90 min": "dde4ed81-211f-4d7f-a5c6-9aa7c9236a77",
        "Kolageni tretman lica - 120 min": "d0dc9749-ac9a-4d89-9bfb-81e9d31d773c",
        "Kolageni tretman lica - 60 min": "99348133-56af-49b9-bb6c-93bf5e6c24c5",
        "Kolageni tretman lica - 90 min": "df17ac96-2006-4df5-96ab-119cac5696d0",
        "Kombinovani spa dan - 120 min": "0f479cc1-564c-44f4-9a48-0cfd66b24fec",
        "Kombinovani spa dan - 60 min": "e83822fd-2f7a-4f92-a622-0765b6ea7311",
        "Kombinovani spa dan - 90 min": "adc6a5d5-4e3d-4518-a42f-89d0c517bfca",
        "Glava, vrat, ramena i leđa - 30 min": "f3dc4924-0a60-444b-be0b-62df5582a717",
        "Glava, vrat, ramena i leđa - 45 min": "b8e8f701-4c47-4772-8cb1-0a1d5a9103e6",
        "Glava, vrat, ramena i leđa - 60 min": "b0a30ca6-7758-48d5-9f21-51f3e82c3d36",
        "Kraljevski spa paket - 120 min": "4a390175-9f3a-4c94-bce3-082623a7a4ce",
        "Kraljevski spa paket - 60 min": "1274dac4-3027-49b6-a737-d800d82d30d7",
        "Kraljevski spa paket - 90 min": "b9a70d94-4db5-43ff-bd63-694fe3712536",
        "Limfna drenaža - 120 min": "76855d35-ad78-48d6-bf51-83f12889bbac",
        "Limfna drenaža - 60 min": "a7e3305f-9e42-4dc5-b3a2-98ab16609f2b",
        "Limfna drenaža - 90 min": "149ccfa1-7336-4512-8a9e-1e6c723fbd72",
        "Masaža dubokih tkiva - 120 min": "04818cf0-d4b3-4f4e-acec-c8b733707da5",
        "Masaža dubokih tkiva - 60 min": "9e713249-bb89-4ff6-9d36-fd1d79423dc9",
        "Masaža dubokih tkiva - 90 min": "9a14d4f0-9f9c-4bdf-90e7-1fd3e9bfeca3",
        "Masaža leđa i vrata - 120 min": "983d4f8c-a824-45b2-a080-b49f5623c128",
        "Masaža leđa i vrata - 60 min": "1a940993-d461-4d99-8c2f-4e47347e7fe3",
        "Masaža leđa i vrata - 90 min": "7721ac2f-1d69-4cc7-88bd-5060661dcf74",
        "Masaža stopala - 30 min": "c4f3d344-73f9-4a0d-ae39-6f2be718ef19",
        "Masaža stopala - 45 min": "73e1cbf7-f6e7-44c5-abfc-070c5e57e844",
        "Masaža stopala - 60 min": "3e45f6f3-3448-41d0-9686-9d3fa5d0414d",
        "Masaža toplim uljem - 60 min": "5d6f85c8-d22e-4cc3-b91a-44baa8ab10d3",
        "Masaža toplim uljem - 90 min": "b82bac9b-318c-4db8-8bb0-28bec7d079d7",
        "Parno kupatilo - 120 min": "f1d62916-c7af-46d5-b719-f914f179586d",
        "Parno kupatilo - 60 min": "486dbba1-a2e2-4c68-b595-ab3a85814828",
        "Parno kupatilo - 90 min": "28ef84b4-aa81-4021-b342-dea1943a0864",
        "Aroma duboko tkivo - 60 min": "7670cc90-65c2-4a07-8caa-e12f646ca00f",
        "Aroma duboko tkivo - 90 min": "3fb7dce2-a7ab-44e9-be08-b729d969b49c",
        "Piling tela - 120 min": "ba22cf25-8b1f-49b4-9f16-454ba343ea17",
        "Piling tela - 60 min": "645ee9fd-6f2a-4d7f-b285-2e243638073b",
        "Piling tela - 90 min": "9b7d8546-a530-467b-b923-4c8e27a7b39a",
        "Prenatalna masaža - 120 min": "03b135d8-9636-48f1-836f-e82c0e014505",
        "Prenatalna masaža - 60 min": "5f7434ec-9afe-4382-93f3-3cca2219eec1",
        "Prenatalna masaža - 90 min": "fa90add4-8fb7-49c5-bae7-a6d23d287cf2",
        "Refleksologija - 120 min": "3b470877-873e-4087-b9a9-dc7de71ee63a",
        "Refleksologija - 60 min": "1bc0bb1d-1fc0-4657-b0c0-5da9d7be92ae",
        "Refleksologija - 90 min": "ecb379ec-345f-498c-8714-44e3d97ed111",
        "Shiatsu masaža - 120 min": "4ad05565-5ee7-4bbb-8fa7-74af92751479",
        "Shiatsu masaža - 60 min": "1077aa29-6207-458d-88ed-f4c8544a0c81",
        "Shiatsu masaža - 90 min": "86585b7f-99ae-4398-bd03-e4d4361e57ab",
        "Sportska masaža - 120 min": "d3e8684a-2bbc-4a15-835e-8e43d231074a",
        "Sportska masaža - 60 min": "3fe475c2-19be-48f6-bebc-0144feecaf94",
        "Sportska masaža - 90 min": "2c389b61-b655-4d74-a254-469a28d3f32a",
        "Masaža za parove - 120 min": "d3e8684a-2bbc-4a15-835e-8e43d231074a",
        "Masaža za parove - 60 min": "3fe475c2-19be-48f6-bebc-0144feecaf94",
        "Masaža za parove - 90 min": "2c389b61-b655-4d74-a254-469a28d3f32a",
        "Tradicionalna tajlandska masaža - 120 min": "b05c9522-30e8-4841-854c-2bec395a61ff",
        "Tradicionalna tajlandska masaža - 60 min": "f3c55c37-5366-4be2-a47a-12322ef735fd",
        "Tradicionalna tajlandska masaža - 90 min": "39f8c583-a780-4e54-9bab-f693a51287c2",
        "Tretman lica - 120 min": "b78fa719-0020-4987-be95-47f7ea65e70a",
        "Tretman lica - 60 min": "75c1c431-b9aa-4ed6-acc5-b2498eb8ccaf",
        "Tretman lica - 90 min": "d6bf13ca-d99c-48b9-8137-bc915a3da4f6",
        "Vitamin C tretman lica - 120 min": "69837aa1-7f27-4b79-bb43-a35c9ed7b662",
        "Vitamin C tretman lica - 60 min": "a2274064-9518-4d7e-af20-10ebf3b555b5",
        "Vitamin C tretman lica - 90 min": "d56f239b-c74c-4cf1-bf1f-33b84d503575",
        "Zlatni tretman lica - 120 min": "a094b37c-4c5b-4554-b0ea-ffb694d0b012",
        "Zlatni tretman lica - 60 min": "5290a732-ea32-400f-b6c8-0a3d985e425f",
        "Zlatni tretman lica - 90 min": "7cc4d292-5d54-42f0-b511-1fb4263f6353",
        "Čokoladni wrap - 120 min": "ad7d2a96-3f05-495d-8939-96dcf47501fb",
        "Čokoladni wrap - 60 min": "b5374198-efb2-4c28-b5fb-fd61207b77e7",
        "Čokoladni wrap - 90 min": "c2c079a0-e906-4f32-ac85-8fc4a650316b"
      };
      
      // Get service UUID from mapping (use serviceLookupName for couples massage)
      const serviceId = serviceMapping[serviceLookupName];
      
      // CRITICAL: Validate service exists in mapping
      if (!serviceId) {
        console.error('❌ SERVICE NOT FOUND IN MAPPING!', {
          serviceName,
          serviceLookupName,
          availableServices: Object.keys(serviceMapping).filter(k => k.includes(serviceName.split(' - ')[0]))
        });
        setError(translate("error") || "Došlo je do greške");
        setIsSubmitting(false);
        return;
      }
      
      // Debug logging
      console.log('📌 Booking Debug:', {
        serviceName,
        serviceLookupName,
        serviceId,
        found: true
      });
      
      // Only send to booking API if we have date and time
      if (formData.preferredDate && formData.preferredTime) {
        // Convert Date object to YYYY-MM-DD format using local time (Belgrade timezone)
        let dateStr;
        if (formData.preferredDate instanceof Date) {
          const year = formData.preferredDate.getFullYear();
          const month = String(formData.preferredDate.getMonth() + 1).padStart(2, '0');
          const day = String(formData.preferredDate.getDate()).padStart(2, '0');
          dateStr = `${year}-${month}-${day}`;
        } else {
          dateStr = formData.preferredDate;
        }
        
        // Prepare data for API
        const appointmentData = {
          client_first_name: formData.firstName,
          client_last_name: formData.lastName,
          client_phone: formData.phone,
          client_email: formData.email,
          appointment_date: dateStr,
          start_time: `${dateStr}T${formData.preferredTime}:00`, // Combine date and time
          service_id: serviceId,
          therapist_id: "1490364f-31c8-49a6-a370-2e19fed34e81", // Generic therapist for web bookings - owner assigns real therapist in salon
          notes: formData.message || "",
          language: language, // Send current language for email
          service_name: serviceName // Send service name for email display
        };

        // Use backend proxy for booking
        const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
        const response = await fetch(`${backendUrl}/api/book-appointment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(appointmentData)
        });

        if (!response.ok) {
          throw new Error('Failed to book appointment');
        }
      }

      // Success - show green checkmark with appropriate message
      setSubmitStatus('success');
      
      // Format date for email
      const emailDate = formData.preferredDate instanceof Date
        ? formatDate(formData.preferredDate.toISOString().split('T')[0])
        : (formData.preferredDate ? formatDate(formData.preferredDate) : 'Nije navedeno');
      
      // Also send email as backup
      const subject = encodeURIComponent(`Rezervacija tretmana - ${formData.firstName} ${formData.lastName}`);
      const body = encodeURIComponent(
        `Ime: ${formData.firstName} ${formData.lastName}\n` +
        `Telefon: ${formData.phone}\n` +
        `Email: ${formData.email}\n` +
        `Usluga: ${serviceName}\n` +
        `Željeni datum: ${emailDate}\n` +
        `Željeno vreme: ${formData.preferredTime || 'Nije navedeno'}\n\n` +
        `Poruka:\n${formData.message}`
      );
      
      const mailtoLink = `mailto:bualuangthailandspa@gmail.com?subject=${subject}&body=${body}`;
      window.location.href = mailtoLink;
      
      // Reset form after 2 seconds
      setTimeout(() => {
        setFormData({
          firstName: "",
          lastName: "",
          phone: "",
          email: "",
          message: "",
          preferredDate: null,
          preferredTime: "",
          source: "message"
        });
        setSubmitStatus(null);
      }, 2000);
      
    } catch (error) {
      console.error('Booking error:', error);
      // Error - show red X
      setSubmitStatus('error');
      
      // Hide error after 2 seconds
      setTimeout(() => {
        setSubmitStatus(null);
      }, 2000);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="contact-container">
      {/* Header */}
      <section className="page-header">
        <div className="page-header-content">
          <h1 className="page-title">BOOKING</h1>
        </div>
        <div className="page-decoration contact-logo-animation">
          <img 
            src="https://customer-assets.emergentagent.com/job_serene-retreat-1/artifacts/r2vm59ex_Bualuang%20logo%20senka.png"
            alt="Bua Luang Thai Spa Logo"
            className="contact-animated-logo"
          />
        </div>
      </section>

      {/* Unified Contact Card */}
      <section className="contact-section">
        <Card className="unified-contact-card">
          <CardContent className="unified-contact-content" style={{ padding: '2rem' }}>
            <div style={{ 
              display: 'flex', 
              gap: '2rem', 
              alignItems: 'flex-start',
              justifyContent: 'space-between'
            }}>
              {/* Contact Form Section - Left Side */}
              <div style={{ flex: '0 0 55%', maxWidth: '55%' }}>
                <form onSubmit={handleSubmit} className="unified-contact-form">
                <div className="form-row">
                  <div className="form-group">
                    <Label htmlFor="firstName">{translate("firstName")}</Label>
                    <Input
                      id="firstName"
                      name="firstName"
                      type="text"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("firstName")}
                    />
                  </div>
                  <div className="form-group">
                    <Label htmlFor="lastName">{translate("lastName")}</Label>
                    <Input
                      id="lastName"
                      name="lastName"
                      type="text"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("lastName")}
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <Label htmlFor="phone">{translate("phone")}</Label>
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("phone")}
                    />
                  </div>
                  <div className="form-group">
                    <Label htmlFor="email">{translate("email")}</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("email")}
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <Label htmlFor="preferredDate">
                      <Calendar className="w-4 h-4 inline mr-2" />
                      {translate("preferredDate")}
                    </Label>
                    <div style={{ width: '100%' }}>
                      <CustomCalendarModal
                        value={formData.preferredDate}
                        onChange={handleDateChange}
                        name="preferredDate"
                        minDate={new Date()}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <Label htmlFor="preferredTime">
                      <Clock className="w-4 h-4 inline mr-2" />
                      {translate("preferredTime")}
                    </Label>
                    <div style={{ width: '100%' }}>
                      <CustomTimePickerModal
                        value={formData.preferredTime}
                        onChange={handleInputChange}
                        name="preferredTime"
                      />
                    </div>
                  </div>
                </div>
                
                {/* Service Dropdown - if no service selected from card */}
                {!new URLSearchParams(location.search).get('service') && (
                  <div className="form-group">
                    <Label htmlFor="serviceDropdown">
                      <span style={{ fontSize: '1rem', fontWeight: '600' }}>
                        {translate("selectService") || "Izaberite uslugu"}
                      </span>
                    </Label>
                    <select
                      id="serviceDropdown"
                      name="serviceDropdown"
                      value={formData.service || ''}
                      onChange={(e) => {
                        const selectedValue = e.target.value; // This is "serviceKey|duration"
                        if (selectedValue) {
                          const [serviceKey, duration] = selectedValue.split('|');
                          const bookingName = bookingSystemNames[serviceKey];
                          const fullServiceName = `${bookingName} - ${duration} min`;
                          const displayName = e.target.options[e.target.selectedIndex].text;
                          
                          setFormData(prev => ({
                            ...prev,
                            service: fullServiceName, // Serbian name for booking API
                            message: `${translate('wantToBook')} ${displayName}`
                          }));
                        } else {
                          setFormData(prev => ({
                            ...prev,
                            service: '',
                            message: ''
                          }));
                        }
                      }}
                      style={{
                        width: '100%',
                        padding: '0.75rem 1rem',
                        border: '1px solid #444',
                        borderRadius: '8px',
                        background: 'rgba(0, 0, 0, 0.3)',
                        color: '#d4af37',
                        fontSize: '1rem',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <option value="" style={{ background: '#1a1a1a', color: '#999' }}>
                        -- {translate("chooseService") || "Odaberite uslugu"} --
                      </option>
                      
                      <optgroup label={translate("massages") || "MASAŽE"} style={{ background: '#1a1a1a', color: '#d4af37', fontWeight: 'bold' }}>
                        {massageServices.map(service => {
                          // Special handling for Aroma duboko tkivo (couplesMassage) - only 60 and 90 min
                          let availableDurations = durations;
                          if (service.key === 'couplesMassage') {
                            availableDurations = [
                              { minutes: 60, price: 4900 },
                              { minutes: 90, price: 6000 }
                            ];
                          }
                          
                          return availableDurations.map(dur => {
                            const serviceName = bookingSystemNames[service.key];
                            const displayValue = `${serviceName} - ${dur.minutes} min - ${dur.price.toLocaleString()} RSD`;
                            const dataValue = `${service.key}|${dur.minutes}`; // key|duration
                            return (
                              <option 
                                key={`${service.key}-${dur.minutes}`}
                                value={dataValue}
                                data-display={displayValue}
                                style={{ background: '#1a1a1a', color: '#d4af37' }}
                              >
                                {displayValue}
                              </option>
                            );
                          });
                        })}
                      </optgroup>
                      
                      <optgroup label={translate("spaTreatments") || "SPA TRETMANI"} style={{ background: '#1a1a1a', color: '#d4af37', fontWeight: 'bold' }}>
                        {spaServices.map(service => (
                          durations.map(dur => {
                            const serviceName = translate(service.key);
                            const displayValue = `${serviceName} - ${dur.minutes} min - ${dur.price.toLocaleString()} RSD`;
                            const dataValue = `${service.key}|${dur.minutes}`; // key|duration
                            return (
                              <option 
                                key={`${service.key}-${dur.minutes}`}
                                value={dataValue}
                                data-display={displayValue}
                                style={{ background: '#1a1a1a', color: '#d4af37' }}
                              >
                                {displayValue}
                              </option>
                            );
                          })
                        ))}
                      </optgroup>
                    </select>
                  </div>
                )}
                
                <div className="form-group">
                  <Label htmlFor="message">{translate("message")}</Label>
                  <Textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    required
                    rows={5}
                    className="form-textarea"
                    placeholder={translate("messagePlaceholder")}
                  />
                </div>
                
                {/* Success/Error Feedback */}
                {submitStatus && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '1rem',
                    borderRadius: '8px',
                    backgroundColor: submitStatus === 'success' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    border: `2px solid ${submitStatus === 'success' ? '#22c55e' : '#ef4444'}`,
                    marginBottom: '1rem'
                  }}>
                    {submitStatus === 'success' ? (
                      <>
                        <svg style={{ width: '32px', height: '32px', color: '#22c55e', marginRight: '0.5rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                        <span style={{ color: '#22c55e', fontWeight: 'bold', fontSize: '1.1rem' }}>
                          {formData.source === 'voucher' ? translate("successVoucher") : 
                           formData.source === 'booking' ? translate("successBooking") : 
                           translate("successMessage")}
                        </span>
                      </>
                    ) : (
                      <>
                        <svg style={{ width: '32px', height: '32px', color: '#ef4444', marginRight: '0.5rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        <span style={{ color: '#ef4444', fontWeight: 'bold', fontSize: '1.1rem' }}>
                          Greška! Molimo pokušajte ponovo.
                        </span>
                      </>
                    )}
                  </div>
                )}
                
                <Button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="submit-button"
                >
                  <Send className="w-4 h-4 mr-2" />
                  {isSubmitting ? "Šalje se..." : translate("send")}
                </Button>
              </form>
            </div>

            {/* Booking Information Section - Right Side */}
            <div style={{ flex: '0 0 40%', maxWidth: '40%' }}>
              <h3 style={{ 
                color: 'var(--spa-gold)', 
                fontSize: '1.5rem', 
                marginBottom: '1.5rem',
                fontWeight: 'bold'
              }}>
                {translate("bookingInfoTitle")}
              </h3>
              <div className="unified-booking-details">
                <div className="unified-booking-item" style={{
                  marginBottom: '1.5rem',
                  padding: '1rem',
                  backgroundColor: 'rgba(212, 175, 55, 0.05)',
                  borderLeft: '3px solid var(--spa-gold)',
                  borderRadius: '4px'
                }}>
                  <h4 style={{ color: 'var(--spa-gold)', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    {translate("cancellationTitle")}
                  </h4>
                  <p style={{ color: 'rgba(245, 242, 232, 0.9)', lineHeight: '1.6' }}>
                    {translate("cancellationText")}
                  </p>
                </div>
                <div className="unified-booking-item" style={{
                  marginBottom: '1.5rem',
                  padding: '1rem',
                  backgroundColor: 'rgba(212, 175, 55, 0.05)',
                  borderLeft: '3px solid var(--spa-gold)',
                  borderRadius: '4px'
                }}>
                  <h4 style={{ color: 'var(--spa-gold)', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    {translate("lateArrivalTitle")}
                  </h4>
                  <p style={{ color: 'rgba(245, 242, 232, 0.9)', lineHeight: '1.6' }}>
                    {translate("lateArrivalText")}
                  </p>
                </div>
                <div className="unified-booking-item" style={{
                  padding: '1rem',
                  backgroundColor: 'rgba(212, 175, 55, 0.05)',
                  borderLeft: '3px solid var(--spa-gold)',
                  borderRadius: '4px'
                }}>
                  <h4 style={{ color: 'var(--spa-gold)', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    {translate("groupBookingTitle")}
                  </h4>
                  <p style={{ color: 'rgba(245, 242, 232, 0.9)', lineHeight: '1.6' }}>
                    {translate("groupBookingText")}
                  </p>
                </div>
              </div>
            </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

export default Contact;