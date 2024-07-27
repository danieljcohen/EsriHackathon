import { Component, Element, VNode, h } from '@stencil/core';
import '@esri/calcite-components';

@Component({
  tag: 'arcgis-asset-tracker',
  styleUrl: 'arcgis-asset-tracker.scss',
  shadow: true,
})
export class ArcgisAssetTracker {
  @Element() hostElement: HTMLArcgisAssetTrackerElement;

  //--------------------------------------------------------------------------
  //
  //  Properties
  //
  //--------------------------------------------------------------------------

  //--------------------------------------------------------------------------
  //
  //  Private Properties
  //
  //--------------------------------------------------------------------------

  //--------------------------------------------------------------------------
  //
  //  Lifecycle
  //
  //--------------------------------------------------------------------------

  // --------------------------------------------------------------------------
  //
  //  Renderer methods
  //
  // --------------------------------------------------------------------------

  render(): VNode {
    return (
      <calcite-panel heading="Arcgis Asset Tracker" scale="l">
        <arcgis-asset-tracker-panel></arcgis-asset-tracker-panel>\
      </calcite-panel>
    );
  }

  // --------------------------------------------------------------------------
  //
  //  Private methods
  //
  // --------------------------------------------------------------------------
}
