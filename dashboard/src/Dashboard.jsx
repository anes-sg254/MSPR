// src/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Filters from './components/Filters';
import StatsCards from './components/StatsCards';
import LineChart from './components/LineChart';
import PieChart from './components/PieChart';
import Histogram from './components/Histogram';
import BarChart from './components/BarChart';
import MapChart from './components/MapChart';

export default function Dashboard() {
    // États principaux
    const [countries, setCountries] = useState([]);
    const [pandemics, setPandemics] = useState([]);
    const [selectedCountry, setSelectedCountry] = useState("");
    const [selectedPandemic, setSelectedPandemic] = useState("");
    const [statType, setStatType] = useState('daily_new_cases');
    const [startDate, setStartDate] = useState("2020-01-01");
    const [endDate, setEndDate] = useState("2025-01-01");

    // Données chiffrées
    const [stats, setStats] = useState({
        total_confirmed: 0,
        total_deaths: 0,
        total_recovered: 0,
        population: 0
    });
    const [mortalityRate, setMortalityRate] = useState(0);
    const [transmissionRate, setTransmissionRate] = useState(0);

    // Données journalières
    const [dailyData, setDailyData] = useState([]);

    // Agrégation par continent
    const [byContinent, setByContinent] = useState([]);

    // Agrégation par pays (pour la carte)
    const [byCountry, setByCountry] = useState([]);

    // Charger la liste des pays et pandémies au montage
    useEffect(() => {
        axios.get('http://127.0.0.1:5000/country')
            .then(res => setCountries(res.data))
            .catch(err => console.error("Erreur country:", err));

        axios.get('http://127.0.0.1:5000/pandemic')
            .then(res => setPandemics(res.data))
            .catch(err => console.error("Erreur pandemic:", err));
    }, []);

    // Récupérer stats et données journalières lors du changement de sélection et de période
    useEffect(() => {
        if (!selectedCountry || !selectedPandemic) {
            setStats({
                total_confirmed: 0,
                total_deaths: 0,
                total_recovered: 0,
                population: 0
            });
            setDailyData([]);
            setMortalityRate(0);
            setTransmissionRate(0);
            return;
        }

        axios.get(`http://127.0.0.1:5000/pandemic_country/${selectedCountry}/${selectedPandemic}`)
            .then(res => {
                const d = res.data;
                setStats({
                    total_confirmed: d.total_confirmed || 0,
                    total_deaths: d.total_deaths || 0,
                    total_recovered: d.total_recovered || 0,
                    population: d.population || 0
                });
                const rateMort = d.total_confirmed ? (d.total_deaths / d.total_confirmed) * 100 : 0;
                setMortalityRate(rateMort.toFixed(2));
            })
            .catch(err => console.error("Erreur totaux:", err));

        axios.get(`http://127.0.0.1:5000/daily_pandemic_country/${selectedCountry}/${selectedPandemic}`)
            .then(res => {
                const filt = res.data.filter(entry => {
                    const d = new Date(entry.date);
                    return d >= new Date(startDate) && d <= new Date(endDate);
                });
                setDailyData(filt);
                const totalCases = filt.reduce((sum, x) => sum + (x.daily_new_cases || 0), 0);
                const meanActive = filt.length
                    ? filt.reduce((sum, x) => sum + (x.active_cases || 0), 0) / filt.length
                    : 0;
                const trans = meanActive ? (totalCases / meanActive) * 100 : 0;
                setTransmissionRate(trans.toFixed(2));
            })
            .catch(err => console.error("Erreur dailyData:", err));
    }, [selectedCountry, selectedPandemic, startDate, endDate]);

    // Récupérer l'agrégation par continent
    useEffect(() => {
        axios.get(`http://127.0.0.1:5000/pandemic_country/continent`)
            .then(res => setByContinent(res.data))
            .catch(err => console.error("Erreur byContinent:", err));
    }, [statType]);

    // Récupérer l'agrégation par pays pour la carte
    useEffect(() => {
        axios.get('http://127.0.0.1:5000/pandemic_country/countries')
            .then(res => {
                const transformed = res.data.map(item => ({
                    countryCode: item.countryCode,
                    lat: item.lat,
                    long: item.long,
                    value:
                        statType === 'daily_new_cases'
                            ? item.daily_new_cases
                            : item.daily_deaths,
                }));
                setByCountry(transformed);
            })
            .catch(err => console.error("Erreur byCountry :", err));
    }, [statType]);

    return (
        <div className="min-h-screen bg-gray-900 text-white p-4">
            {/* Header */}
            <header className="mb-6">
                <h1 className="text-3xl font-bold text-center">Tableau de bord Pandémies</h1>
            </header>

            {/* Conteneur principal responsive : column sur mobile, row à partir de md */}
            <div className="flex flex-col md:flex-row items-start">
                {/* Colonne de gauche : Filters */}
                <Filters
                    countries={countries}
                    pandemics={pandemics}
                    selectedCountry={selectedCountry}
                    setSelectedCountry={setSelectedCountry}
                    selectedPandemic={selectedPandemic}
                    setSelectedPandemic={setSelectedPandemic}
                    statType={statType}
                    setStatType={setStatType}
                    startDate={startDate}
                    setStartDate={setStartDate}
                    endDate={endDate}
                    setEndDate={setEndDate}
                />

                {/* Contenu principal */}
                <div className="flex-1 space-y-8 mt-6 md:mt-0 md:ml-6">
                    <StatsCards
                        stats={stats}
                        mortalityRate={mortalityRate}
                        transmissionRate={transmissionRate}
                    />

                    <section aria-label="Visualisations interactives" className="space-y-8">
                        {/* passe à 2 colonnes sur lg+ */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="space-y-8">
                                <LineChart dailyData={dailyData} statType={statType} />
                                <Histogram dailyData={dailyData} statType={statType} />
                            </div>
                            <div className="space-y-8">
                                <PieChart byContinent={byContinent} statType={statType} />
                                <BarChart byContinent={byContinent} statType={statType} />
                            </div>
                        </div>
                    </section>

                    {/* Ajout de la carte du monde en dessous des graphiques existants */}
                    <section className="mt-8">
                        <MapChart byCountry={byCountry} statType={statType} />
                    </section>
                </div>
            </div>
        </div>
    );
}
