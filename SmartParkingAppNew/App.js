// Smart Parking Mobile App - React Native
// File: App.js

import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

const API_BASE_URL = 'http://192.168.29.106:5000/api';
const { width } = Dimensions.get('window');

// API Service
class ParkingAPI {
  static async getStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/status`);
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  static async updateParking() {
    try {
      const response = await fetch(`${API_BASE_URL}/update`, {
        method: 'POST',
      });
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  static async findParking(destination = 'main_entrance') {
    try {
      const response = await fetch(`${API_BASE_URL}/find-parking?destination=${destination}`);
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  static async getPricingHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/pricing/history`);
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
}

// Components
const ParkingSpotCard = ({ spot, onPress }) => (
  <TouchableOpacity
    style={[
      styles.spotCard,
      { backgroundColor: spot.is_occupied ? '#e74c3c' : '#27ae60' }
    ]}
    onPress={() => onPress(spot)}
  >
    <Text style={styles.spotNumber}>{spot.spot_number}</Text>
    <Text style={styles.spotStatus}>
      {spot.is_occupied ? 'OCCUPIED' : 'AVAILABLE'}
    </Text>
  </TouchableOpacity>
);

const StatCard = ({ title, value, color = '#3498db' }) => (
  <View style={[styles.statCard, { borderLeftColor: color }]}>
    <Text style={styles.statTitle}>{title}</Text>
    <Text style={styles.statValue}>{value}</Text>
  </View>
);

// Main Dashboard Screen
const DashboardScreen = () => {
  const [parkingData, setParkingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const data = await ParkingAPI.getStatus();
      setParkingData(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load parking data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const handleUpdateDetection = async () => {
    try {
      setLoading(true);
      await ParkingAPI.updateParking();
      await loadData();
      Alert.alert('Success', 'Parking detection updated!');
    } catch (error) {
      Alert.alert('Error', 'Failed to update detection');
      setLoading(false);
    }
  };

  const handleSpotPress = (spot) => {
    Alert.alert(
      `Spot ${spot.spot_number}`,
      `Status: ${spot.is_occupied ? 'Occupied' : 'Available'}\\nLast Updated: ${new Date(spot.last_updated).toLocaleString()}`,
      [{ text: 'OK' }]
    );
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Auto-refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading && !parkingData) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.loadingText}>Loading parking data...</Text>
      </View>
    );
  }

  if (!parkingData) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.errorText}>Failed to load data</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadData}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const occupancyRate = Math.round(parkingData.occupancy_rate * 100);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2c3e50" />
      
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🚗 Smart Parking</Text>
          <Text style={styles.headerSubtitle}>{parkingData.lot_name}</Text>
        </View>

        {/* Stats Section */}
        <View style={styles.statsContainer}>
          <StatCard
            title="Available Spots"
            value={`${parkingData.available_spots}/${parkingData.total_spots}`}
            color="#27ae60"
          />
          <StatCard
            title="Occupancy Rate"
            value={`${occupancyRate}%`}
            color={occupancyRate > 80 ? '#e74c3c' : occupancyRate > 60 ? '#f39c12' : '#27ae60'}
          />
          <StatCard
            title="Current Price"
            value={`$${parkingData.current_price.toFixed(2)}/hr`}
            color="#3498db"
          />
        </View>

        {/* Action Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.actionButton, styles.updateButton]}
            onPress={handleUpdateDetection}
            disabled={loading}
          >
            <Ionicons name="refresh" size={20} color="white" />
            <Text style={styles.buttonText}>Update Detection</Text>
          </TouchableOpacity>
        </View>

        {/* Parking Grid */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>Parking Layout</Text>
          <View style={styles.parkingGrid}>
            {parkingData.spots.map((spot) => (
              <ParkingSpotCard
                key={spot.id}
                spot={spot}
                onPress={handleSpotPress}
              />
            ))}
          </View>
        </View>

        {/* Legend */}
        <View style={styles.legendContainer}>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#27ae60' }]} />
            <Text style={styles.legendText}>Available</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#e74c3c' }]} />
            <Text style={styles.legendText}>Occupied</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// Find Parking Screen
const FindParkingScreen = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const findBestSpot = async () => {
    setLoading(true);
    try {
      const data = await ParkingAPI.findParking();
      setRecommendations(data.recommended_spots || []);
    } catch (error) {
      Alert.alert('Error', 'Failed to find parking spots');
    } finally {
      setLoading(false);
    }
  };

  const handleReserveSpot = (spot) => {
    Alert.alert(
      'Reserve Spot',
      `Would you like to navigate to spot ${spot.spot.spot_number}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Navigate', onPress: () => navigateToSpot(spot) }
      ]
    );
  };

  const navigateToSpot = (spot) => {
    // In a real app, this would integrate with navigation
    Alert.alert(
      'Navigation',
      `Navigating to spot ${spot.spot.spot_number}...\\n\\nIn a real implementation, this would open your preferred navigation app.`
    );
  };

  useEffect(() => {
    findBestSpot();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🎯 Find Parking</Text>
          <Text style={styles.headerSubtitle}>AI-Recommended Spots</Text>
        </View>

        <TouchableOpacity
          style={[styles.actionButton, styles.findButton]}
          onPress={findBestSpot}
          disabled={loading}
        >
          <Ionicons name="search" size={20} color="white" />
          <Text style={styles.buttonText}>
            {loading ? 'Finding...' : 'Find Best Spots'}
          </Text>
        </TouchableOpacity>

        {recommendations.length > 0 && (
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>Recommended Spots</Text>
            {recommendations.map((rec, index) => (
              <TouchableOpacity
                key={rec.spot.id}
                style={styles.recommendationCard}
                onPress={() => handleReserveSpot(rec)}
              >
                <View style={styles.recommendationHeader}>
                  <Text style={styles.recommendationSpot}>
                    Spot {rec.spot.spot_number}
                  </Text>
                  <Text style={styles.recommendationScore}>
                    Score: {rec.score.toFixed(1)}/10
                  </Text>
                </View>
                <Text style={styles.recommendationDetail}>
                  Confidence: {Math.round(rec.prediction.confidence * 100)}%
                </Text>
                {rec.prediction.occupancy_rate && (
                  <Text style={styles.recommendationDetail}>
                    Historical occupancy: {Math.round(rec.prediction.occupancy_rate * 100)}%
                  </Text>
                )}
                <View style={styles.recommendationFooter}>
                  <Text style={styles.recommendationRank}>#{index + 1} Recommended</Text>
                  <Ionicons name="arrow-forward" size={16} color="#3498db" />
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {recommendations.length === 0 && !loading && (
          <View style={styles.centeredContainer}>
            <Text style={styles.noDataText}>No recommendations available</Text>
            <Text style={styles.noDataSubtext}>Try refreshing or check back later</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

// Analytics Screen
const AnalyticsScreen = () => {
  const [pricingHistory, setPricingHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadPricingData = async () => {
    try {
      const data = await ParkingAPI.getPricingHistory();
      setPricingHistory(data.pricing_history || []);
    } catch (error) {
      Alert.alert('Error', 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPricingData();
  }, []);

  const getCurrentHour = () => new Date().getHours();
  const currentHour = getCurrentHour();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>📊 Analytics</Text>
          <Text style={styles.headerSubtitle}>Pricing & Occupancy Trends</Text>
        </View>

        {loading ? (
          <View style={styles.centeredContainer}>
            <Text style={styles.loadingText}>Loading analytics...</Text>
          </View>
        ) : (
          <>
            {/* Current Hour Highlight */}
            <View style={styles.currentHourCard}>
              <Text style={styles.currentHourTitle}>Current Hour ({currentHour}:00)</Text>
              {pricingHistory.find(h => h.hour === currentHour) && (
                <>
                  <Text style={styles.currentHourPrice}>
                    ${pricingHistory.find(h => h.hour === currentHour).price.toFixed(2)}/hour
                  </Text>
                  <Text style={styles.currentHourOccupancy}>
                    {Math.round(pricingHistory.find(h => h.hour === currentHour).occupancy_rate * 100)}% occupied
                  </Text>
                </>
              )}
            </View>

            {/* Pricing History */}
            <View style={styles.sectionContainer}>
              <Text style={styles.sectionTitle}>24-Hour Pricing History</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={styles.chartContainer}>
                  {pricingHistory.map((item, index) => (
                    <View key={index} style={styles.chartBar}>
                      <View
                        style={[
                          styles.priceBar,
                          {
                            height: Math.max(20, item.price * 30),
                            backgroundColor: item.hour === currentHour ? '#e74c3c' : '#3498db'
                          }
                        ]}
                      />
                      <Text style={styles.chartLabel}>{item.hour}:00</Text>
                      <Text style={styles.chartPrice}>${item.price.toFixed(2)}</Text>
                    </View>
                  ))}
                </View>
              </ScrollView>
            </View>

            {/* Occupancy Trends */}
            <View style={styles.sectionContainer}>
              <Text style={styles.sectionTitle}>Occupancy Trends</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={styles.chartContainer}>
                  {pricingHistory.map((item, index) => (
                    <View key={index} style={styles.chartBar}>
                      <View
                        style={[
                          styles.occupancyBar,
                          {
                            height: Math.max(10, item.occupancy_rate * 100),
                            backgroundColor: item.occupancy_rate > 0.8 ? '#e74c3c' : 
                                           item.occupancy_rate > 0.6 ? '#f39c12' : '#27ae60'
                          }
                        ]}
                      />
                      <Text style={styles.chartLabel}>{item.hour}:00</Text>
                      <Text style={styles.chartOccupancy}>
                        {Math.round(item.occupancy_rate * 100)}%
                      </Text>
                    </View>
                  ))}
                </View>
              </ScrollView>
            </View>

            {/* Insights */}
            <View style={styles.sectionContainer}>
              <Text style={styles.sectionTitle}>AI Insights</Text>
              <View style={styles.insightCard}>
                <Text style={styles.insightTitle}>🕒 Peak Hours</Text>
                <Text style={styles.insightText}>
                  Highest occupancy typically between 9 AM - 5 PM
                </Text>
              </View>
              <View style={styles.insightCard}>
                <Text style={styles.insightTitle}>💰 Best Value</Text>
                <Text style={styles.insightText}>
                  Lowest prices usually after 10 PM and before 7 AM
                </Text>
              </View>
              <View style={styles.insightCard}>
                <Text style={styles.insightTitle}>📈 Dynamic Pricing</Text>
                <Text style={styles.insightText}>
                  Prices automatically adjust based on real-time demand
                </Text>
              </View>
            </View>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

// Navigation Setup
const Tab = createBottomTabNavigator();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;
            if (route.name === 'Dashboard') {
              iconName = focused ? 'grid' : 'grid-outline';
            } else if (route.name === 'Find Parking') {
              iconName = focused ? 'search' : 'search-outline';
            } else if (route.name === 'Analytics') {
              iconName = focused ? 'analytics' : 'analytics-outline';
            }
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#2c3e50',
          tabBarInactiveTintColor: 'gray',
          headerShown: false,
        })}
      >
        <Tab.Screen name="Dashboard" component={DashboardScreen} />
        <Tab.Screen name="Find Parking" component={FindParkingScreen} />
        <Tab.Screen name="Analytics" component={AnalyticsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
};

// Main App Component
export default function App() {
  return <AppNavigator />;
}

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollView: {
    flex: 1,
  },
  centeredContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    backgroundColor: '#2c3e50',
    padding: 20,
    paddingTop: 40,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#bdc3c7',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 15,
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  statTitle: {
    fontSize: 12,
    color: '#7f8c8d',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  buttonContainer: {
    padding: 15,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    gap: 8,
  },
  updateButton: {
    backgroundColor: '#3498db',
  },
  findButton: {
    backgroundColor: '#27ae60',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sectionContainer: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  parkingGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  spotCard: {
    width: (width - 60) / 4,
    aspectRatio: 2,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  spotNumber: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 12,
  },
  spotStatus: {
    color: 'white',
    fontSize: 8,
  },
  legendContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 20,
    padding: 15,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  legendColor: {
    width: 16,
    height: 16,
    borderRadius: 3,
  },
  legendText: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  recommendationCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationSpot: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  recommendationScore: {
    fontSize: 14,
    color: '#27ae60',
    fontWeight: 'bold',
  },
  recommendationDetail: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 4,
  },
  recommendationFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  recommendationRank: {
    fontSize: 12,
    color: '#3498db',
    fontWeight: 'bold',
  },
  currentHourCard: {
    backgroundColor: '#2c3e50',
    margin: 15,
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  currentHourTitle: {
    color: 'white',
    fontSize: 16,
    marginBottom: 10,
  },
  currentHourPrice: {
    color: '#f39c12',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  currentHourOccupancy: {
    color: '#bdc3c7',
    fontSize: 14,
  },
  chartContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingVertical: 20,
    paddingHorizontal: 10,
  },
  chartBar: {
    alignItems: 'center',
    marginHorizontal: 8,
    minWidth: 40,
  },
  priceBar: {
    width: 30,
    borderRadius: 4,
    marginBottom: 8,
  },
  occupancyBar: {
    width: 30,
    borderRadius: 4,
    marginBottom: 8,
  },
  chartLabel: {
    fontSize: 10,
    color: '#7f8c8d',
    marginBottom: 2,
  },
  chartPrice: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  chartOccupancy: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  insightCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
  },
  insightText: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  loadingText: {
    fontSize: 16,
    color: '#7f8c8d',
  },
  errorText: {
    fontSize: 16,
    color: '#e74c3c',
    marginBottom: 15,
  },
  noDataText: {
    fontSize: 16,
    color: '#7f8c8d',
  },
  noDataSubtext: {
    fontSize: 14,
    color: '#bdc3c7',
    marginTop: 5,
  },
  retryButton: {
    backgroundColor: '#3498db',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});