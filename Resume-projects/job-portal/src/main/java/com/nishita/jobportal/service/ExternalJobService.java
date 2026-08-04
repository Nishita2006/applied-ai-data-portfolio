package com.nishita.jobportal.service;
import com.fasterxml.jackson.databind.JsonNode;
import com.nishita.jobportal.dto.ExternalJobResponse;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.HtmlUtils;
import org.springframework.web.util.UriComponentsBuilder;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import java.time.*;
import java.util.*;
@Service public class ExternalJobService {
 private static final String FEED_URL="https://remotive.com/api/remote-jobs";
 private static final Set<String> US_STATES=Set.of("alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan","minnesota","mississippi","missouri","montana","nebraska","nevada","new hampshire","new jersey","new mexico","new york","north carolina","north dakota","ohio","oklahoma","oregon","pennsylvania","rhode island","south carolina","south dakota","tennessee","texas","utah","vermont","virginia","washington","west virginia","wisconsin","wyoming");
 private final RestClient client;
 private final Map<String,CacheEntry> cache=new HashMap<>();
 public ExternalJobService(){SimpleClientHttpRequestFactory requests=new SimpleClientHttpRequestFactory();requests.setConnectTimeout(Duration.ofSeconds(5));requests.setReadTimeout(Duration.ofSeconds(8));client=RestClient.builder().requestFactory(requests).build();}
 public List<ExternalJobResponse> search(String query,String location){String q=clean(query),l=clean(location);return load(q).stream().filter(j->q.isEmpty()||contains(j.title(),q)||contains(j.company(),q)||skillMatches(j.skills(),q)).filter(j->locationMatches(j.location(),l)).limit(24).toList();}
 private synchronized List<ExternalJobResponse> load(String query){CacheEntry existing=cache.get(query);if(existing!=null&&Instant.now().isBefore(existing.expires()))return existing.jobs();try{String uri=UriComponentsBuilder.fromUriString(FEED_URL).queryParam("limit",100).queryParamIfPresent("search",query.isBlank()?Optional.empty():Optional.of(query)).build().encode().toUriString();JsonNode root=client.get().uri(uri).retrieve().body(JsonNode.class);List<ExternalJobResponse> fresh=new ArrayList<>();if(root!=null)for(JsonNode j:root.path("jobs"))fresh.add(map(j));List<ExternalJobResponse> result=List.copyOf(fresh);cache.put(query,new CacheEntry(result,Instant.now().plus(Duration.ofMinutes(15))));return result;}catch(Exception ignored){return existing==null?List.of():existing.jobs();}}
 private boolean locationMatches(String jobLocation,String requested){if(requested.isEmpty())return true;if(contains(jobLocation,requested))return true;String available=clean(jobLocation);if(requested.equals("remote"))return available.contains("worldwide")||available.contains("anywhere");if(US_STATES.contains(requested))return available.matches(".*(usa|united states|north(ern)? america|americas|worldwide|anywhere).*");return false;}
 private ExternalJobResponse map(JsonNode j){String tags="";if(j.path("tags").isArray()){List<String> values=new ArrayList<>();j.path("tags").forEach(t->values.add(t.asText()));tags=String.join(", ",values);}if(tags.isBlank())tags=text(j,"category");return new ExternalJobResponse("remotive-"+text(j,"id"),text(j,"title"),text(j,"company_name"),text(j,"candidate_required_location"),text(j,"job_type").replace('_',' '),tags,plain(text(j,"description")),safeUrl(text(j,"url")),text(j,"publication_date"),"Remotive");}
 private String text(JsonNode n,String f){return n.path(f).asText("").trim();} private String plain(String h){return HtmlUtils.htmlUnescape(h.replaceAll("<[^>]*>"," ").replaceAll("\\s+"," ")).trim();} private String safeUrl(String url){return url.startsWith("https://remotive.com/")?url:"";} private String clean(String v){return v==null?"":v.trim().toLowerCase(Locale.ROOT);} private boolean contains(String v,String p){return v!=null&&v.toLowerCase(Locale.ROOT).contains(p);}
 private boolean skillMatches(String skills,String query){return Arrays.stream(skills.split(",")).map(this::clean).anyMatch(query::equals);}
 private record CacheEntry(List<ExternalJobResponse> jobs,Instant expires){}
}
