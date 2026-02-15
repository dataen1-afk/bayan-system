import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Search, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight,
  ArrowUpDown, ArrowUp, ArrowDown, Filter, X
} from 'lucide-react';

// Professional Data Table Component with Pagination, Search, Sorting, and Filtering
const DataTable = ({
  data = [],
  columns = [],
  searchableColumns = [],
  filterOptions = [],
  renderRow,
  emptyState,
  isRTL = false,
  defaultSort = { key: null, direction: 'desc' },
  itemsPerPageOptions = [10, 25, 50, 100],
  defaultItemsPerPage = 25,
  title,
  description,
  headerActions,
  showSearch = true,
  showFilters = true,
  showPagination = true
}) => {
  const { t } = useTranslation();
  
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(defaultItemsPerPage);
  const [sortConfig, setSortConfig] = useState(defaultSort);
  const [activeFilters, setActiveFilters] = useState({});
  const [showFilterPanel, setShowFilterPanel] = useState(false);

  // Handle sorting
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Filter and sort data
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply search filter
    if (searchQuery.trim() && searchableColumns.length > 0) {
      const query = searchQuery.toLowerCase();
      result = result.filter(item => 
        searchableColumns.some(col => {
          const value = col.accessor(item);
          return value && value.toString().toLowerCase().includes(query);
        })
      );
    }

    // Apply column filters
    Object.entries(activeFilters).forEach(([key, value]) => {
      if (value && value !== 'all') {
        result = result.filter(item => {
          const filterOption = filterOptions.find(f => f.key === key);
          if (filterOption) {
            const itemValue = filterOption.accessor(item);
            return itemValue === value;
          }
          return true;
        });
      }
    });

    // Apply sorting
    if (sortConfig.key) {
      const column = columns.find(col => col.key === sortConfig.key);
      if (column && column.sortAccessor) {
        result.sort((a, b) => {
          const aVal = column.sortAccessor(a);
          const bVal = column.sortAccessor(b);
          
          if (aVal === null || aVal === undefined) return 1;
          if (bVal === null || bVal === undefined) return -1;
          
          if (typeof aVal === 'string') {
            return sortConfig.direction === 'asc' 
              ? aVal.localeCompare(bVal)
              : bVal.localeCompare(aVal);
          }
          
          return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
        });
      }
    }

    return result;
  }, [data, searchQuery, searchableColumns, activeFilters, sortConfig, columns, filterOptions]);

  // Pagination
  const totalPages = Math.ceil(processedData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedData = processedData.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  const handleFilterChange = (key, value) => {
    setActiveFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setActiveFilters({});
    setSearchQuery('');
    setCurrentPage(1);
  };

  const hasActiveFilters = searchQuery || Object.values(activeFilters).some(v => v && v !== 'all');

  // Generate page numbers
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden overflow-x-auto">
      {/* Header */}
      <div className={`px-5 py-4 border-b border-slate-100 ${isRTL ? 'text-right' : 'text-left'}`}>
        <div className={`flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 ${isRTL ? 'lg:flex-row-reverse' : ''}`}>
          {/* Title Section */}
          <div>
            {title && <h2 className="text-lg font-semibold text-slate-900">{title}</h2>}
            {description && <p className="text-sm text-slate-500 mt-0.5">{description}</p>}
          </div>
          
          {/* Search & Actions */}
          <div className={`flex flex-wrap items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            {/* Search Input */}
            {showSearch && searchableColumns.length > 0 && (
              <div className="relative">
                <Search className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 ${isRTL ? 'right-3' : 'left-3'}`} />
                <Input
                  type="text"
                  placeholder={t('searchPlaceholder') || 'Search...'}
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(1);
                  }}
                  className={`w-64 h-9 ${isRTL ? 'pr-10 pl-3' : 'pl-10 pr-3'} text-sm`}
                  data-testid="table-search-input"
                />
              </div>
            )}
            
            {/* Filter Toggle */}
            {showFilters && filterOptions.length > 0 && (
              <Button
                variant={showFilterPanel ? 'default' : 'outline'}
                size="sm"
                onClick={() => setShowFilterPanel(!showFilterPanel)}
                className={`h-9 ${showFilterPanel ? 'bg-bayan-navy' : ''}`}
                data-testid="toggle-filter-btn"
              >
                <Filter className="w-4 h-4 me-1.5" />
                {t('filters')}
                {hasActiveFilters && (
                  <span className="ms-1.5 px-1.5 py-0.5 bg-white/20 rounded text-xs">
                    {Object.values(activeFilters).filter(v => v && v !== 'all').length + (searchQuery ? 1 : 0)}
                  </span>
                )}
              </Button>
            )}
            
            {/* Header Actions */}
            {headerActions}
          </div>
        </div>
        
        {/* Filter Panel */}
        {showFilterPanel && filterOptions.length > 0 && (
          <div className={`mt-4 pt-4 border-t border-slate-100 ${isRTL ? 'text-right' : 'text-left'}`}>
            <div className={`flex flex-wrap items-end gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
              {filterOptions.map((filter) => (
                <div key={filter.key} className="min-w-[160px]">
                  <label className="block text-xs font-medium text-slate-600 mb-1.5">
                    {filter.label}
                  </label>
                  <select
                    value={activeFilters[filter.key] || 'all'}
                    onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                    className="w-full h-9 px-3 text-sm rounded-md border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-bayan-navy/20 focus:border-bayan-navy"
                    data-testid={`filter-${filter.key}`}
                  >
                    <option value="all">{t('all')}</option>
                    {filter.options.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
              
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFilters}
                  className="h-9 text-slate-500 hover:text-slate-700"
                  data-testid="clear-filters-btn"
                >
                  <X className="w-4 h-4 me-1" />
                  {t('clearFilters') || 'Clear'}
                </Button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Table Header */}
      <div 
        className={`hidden lg:flex items-center px-5 py-3 bg-slate-50/80 border-b border-slate-100 text-xs font-semibold text-slate-600 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        {columns.map((column) => (
          <div 
            key={column.key}
            className={`${column.width || 'flex-1'} px-1 ${column.sortAccessor ? 'cursor-pointer hover:text-slate-900 select-none' : ''}`}
            onClick={() => column.sortAccessor && handleSort(column.key)}
          >
            <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
              {column.label}
              {column.sortAccessor && (
                <span className="text-slate-400">
                  {sortConfig.key === column.key ? (
                    sortConfig.direction === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />
                  ) : (
                    <ArrowUpDown className="w-3 h-3" />
                  )}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Table Body */}
      <div className="divide-y divide-slate-100" data-testid="table-body" dir={isRTL ? 'rtl' : 'ltr'}>
        {paginatedData.length === 0 ? (
          emptyState || (
            <div className="text-center py-16 px-4">
              <p className="text-slate-500">{t('noDataFound') || 'No data found'}</p>
            </div>
          )
        ) : (
          paginatedData.map((item, index) => renderRow(item, index, isRTL))
        )}
      </div>

      {/* Pagination Footer */}
      {showPagination && processedData.length > 0 && (
        <div className={`px-5 py-4 border-t border-slate-100 bg-slate-50/50 ${isRTL ? 'text-right' : 'text-left'}`}>
          <div className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 ${isRTL ? 'sm:flex-row-reverse' : ''}`}>
            {/* Results Count & Per Page */}
            <div className={`flex items-center gap-4 text-sm text-slate-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <span>
                {t('showing') || 'Showing'}{' '}
                <span className="font-semibold text-slate-900">{startIndex + 1}</span>
                {' '}-{' '}
                <span className="font-semibold text-slate-900">{Math.min(endIndex, processedData.length)}</span>
                {' '}{t('of') || 'of'}{' '}
                <span className="font-semibold text-slate-900">{processedData.length}</span>
                {' '}{t('results') || 'results'}
              </span>
              
              <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <span className="text-xs text-slate-500">{t('perPage') || 'Per page'}:</span>
                <select
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="h-8 px-2 text-sm rounded border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-bayan-navy/20"
                  data-testid="items-per-page-select"
                >
                  {itemsPerPageOptions.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* Page Navigation */}
            <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
              {/* First Page */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage(1)}
                disabled={currentPage === 1}
                className="h-8 w-8 p-0"
                data-testid="first-page-btn"
              >
                {isRTL ? <ChevronsRight className="w-4 h-4" /> : <ChevronsLeft className="w-4 h-4" />}
              </Button>
              
              {/* Previous Page */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="h-8 w-8 p-0"
                data-testid="prev-page-btn"
              >
                {isRTL ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
              </Button>
              
              {/* Page Numbers */}
              <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                {getPageNumbers().map((page, index) => (
                  page === '...' ? (
                    <span key={`ellipsis-${index}`} className="px-2 text-slate-400">...</span>
                  ) : (
                    <Button
                      key={page}
                      variant={currentPage === page ? 'default' : 'ghost'}
                      size="sm"
                      onClick={() => setCurrentPage(page)}
                      className={`h-8 w-8 p-0 ${currentPage === page ? 'bg-bayan-navy' : ''}`}
                      data-testid={`page-${page}-btn`}
                    >
                      {page}
                    </Button>
                  )
                ))}
              </div>
              
              {/* Next Page */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="h-8 w-8 p-0"
                data-testid="next-page-btn"
              >
                {isRTL ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </Button>
              
              {/* Last Page */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage(totalPages)}
                disabled={currentPage === totalPages}
                className="h-8 w-8 p-0"
                data-testid="last-page-btn"
              >
                {isRTL ? <ChevronsLeft className="w-4 h-4" /> : <ChevronsRight className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
