import React from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Globe } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    // Update document direction for RTL support
    document.documentElement.dir = lng === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lng;
    // Store preference
    localStorage.setItem('language', lng);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" data-testid="language-switcher" className="relative">
          <Globe className="h-5 w-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem 
          onClick={() => changeLanguage('ar')}
          data-testid="lang-arabic"
          className={i18n.language === 'ar' ? 'bg-accent' : ''}
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 640 480">
            <defs>
              <clipPath id="a">
                <path fillOpacity=".7" d="M-85.3 0h682.6v512H-85.3z"/>
              </clipPath>
            </defs>
            <g fillRule="evenodd" strokeWidth="1pt" clipPath="url(#a)" transform="translate(80) scale(.9375)">
              <path fill="#199d00" d="M-128 0h768v512h-768z"/>
              <path fill="#fff" d="M-128 0h768v341.3h-768z"/>
              <path d="m-128 0 0 170.7h768V.0z"/>
              <path fill="#ce1126" d="m-128 0 0 170.7h768V.0z"/>
            </g>
          </svg>
          {t('arabic')}
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => changeLanguage('en')}
          data-testid="lang-english"
          className={i18n.language === 'en' ? 'bg-accent' : ''}
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 640 480">
            <path fill="#012169" d="M0 0h640v480H0z"/>
            <path fill="#FFF" d="m75 0 244 181L562 0h78v62L400 241l240 178v61h-80L320 301 81 480H0v-60l239-178L0 64V0h75z"/>
            <path fill="#C8102E" d="m424 281 216 159v40L369 281h55zm-184 20 6 35L54 480H0l240-179zM640 0v3L391 191l2-44L590 0h50zM0 0l239 176h-60L0 42V0z"/>
            <path fill="#FFF" d="M241 0v480h160V0H241zM0 160v160h640V160H0z"/>
            <path fill="#C8102E" d="M0 193v96h640v-96H0zM273 0v480h96V0h-96z"/>
          </svg>
          {t('english')}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default LanguageSwitcher;
