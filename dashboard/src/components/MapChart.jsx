// src/components/MapChart.jsx
import React, { useMemo } from 'react';
import World from '@react-map/world';
import { geoMercator } from 'd3-geo';

/**
 * byCountry : Array<{
 *   countryCode: string,
 *   lat: number,
 *   long: number,
 *   value: number
 * }>
 * statType   : "daily_new_cases" | "daily_deaths"
 */
export default function MapChart({ byCountry, statType }) {
    // Taille (en px) du carré SVG pour la carte
    const size = 800;

    // Calculer la valeur maximale (pour normaliser les rayons)
    const maxValue = useMemo(
        () => byCountry.reduce((max, c) => Math.max(max, c.value || 0), 0),
        [byCountry]
    );

    // Projection Mercator : adapter scale et translate pour un SVG de taille donnée
    // La formule scale = size / (2π) est une approximation courante pour centrer la carte
    const projection = useMemo(
        () =>
            geoMercator()
                .scale(size / (2 * Math.PI))
                .translate([size / 2, size / 2]),
        [size]
    );

    return (
        <div
            className="relative mx-auto"
            style={{ width: '100%', maxWidth: `${size}px`, height: `${size}px` }}
        >
            {/* Carte du monde générée par @react-map/world */}
            <World
                type="select-single"
                size={size}
                mapColor="#374151"
                strokeColor="#4B5563"
                strokeWidth={0.5}
                hoverColor="#6B7280"
                hints={false}
            // Les props ci-dessus sont optionnelles : vous pouvez personnaliser les couleurs et l'affichage
            />

            {/* SVG superposé pour afficher les cercles (pointer-events:none pour laisser passer les clics à la carte) */}
            <svg
                width={size}
                height={size}
                className="absolute top-0 left-0 pointer-events-none"
            >
                {byCountry.map((country) => {
                    const { countryCode, lat, long, value } = country;
                    if (lat == null || long == null || value == null || value <= 0) {
                        return null;
                    }
                    // Projeter (long, lat) en (x, y)
                    const [x, y] = projection([long, lat]);

                    // Calculer rayon : on garantit un minimum pour que les très petits points restent visibles
                    const radius =
                        maxValue > 0
                            ? Math.max(2, (Math.sqrt(value / maxValue) * 20))
                            : 0;

                    return (
                        <circle
                            key={countryCode}
                            cx={x}
                            cy={y}
                            r={radius}
                            fill={
                                statType === 'daily_new_cases'
                                    ? 'rgba(59, 130, 246, 0.7)'
                                    : 'rgba(239, 68, 68, 0.7)'
                            }
                            stroke="#FFFFFF"
                            strokeWidth={0.5}
                        />
                    );
                })}
            </svg>
        </div>
    );
}
